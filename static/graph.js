let network = null;
let nodeDataSet = null;
let edgeDataSet = null;
let activeTopic = null;
let topicsList = [];
let topicToIndex = {};

document.addEventListener("DOMContentLoaded", function () {
    const data = JSON.parse(localStorage.getItem("data"));
    if (!data || !data.graph) return;

    renderGraph(data);
});

function goBack() {
    window.location.href = "/dashboard";
}

function getPrerequisitesMap(graph) {
    const map = {};
    if (!graph || !graph.topics) return map;
    graph.topics.forEach(t => map[t] = []);
    if (graph.edges) {
        graph.edges.forEach(([src, dst]) => {
            if (map[dst]) map[dst].push(src);
        });
    }
    return map;
}

function renderGraph(data) {
    const container = document.getElementById("graph");
    if (!container) return;

    const graphData = data.graph;
    topicsList = graphData.topics || [];
    topicToIndex = Object.fromEntries(topicsList.map((t, i) => [t, i]));

    // ---------------- NODES ----------------
    const nodes = topicsList.map((t, i) => {
        return {
            id: i,
            label: t,
            shape: "dot",
            size: 22,
            font: {
                size: 13,
                color: "#cbd5e1",
                face: "Inter, Outfit, Segoe UI, sans-serif",
                vadjust: 6
            },
            color: {
                background: "#38bdf8",
                border: "#0ea5e9",
                highlight: {
                    background: "#7dd3fc",
                    border: "#38bdf8"
                },
                hover: {
                    background: "#7dd3fc",
                    border: "#38bdf8"
                }
            },
            borderWidth: 2
        };
    });

    // ---------------- EDGES ----------------
    const edges = graphData.edges
        .map(([src, dst]) => {
            return {
                from: topicToIndex[src],
                to: topicToIndex[dst],
                arrows: "to",
                color: {
                    color: "rgba(56, 189, 248, 0.4)",
                    highlight: "#38bdf8"
                },
                width: 2,
                smooth: {
                    type: "continuous",
                    roundness: 0.5
                }
            };
        })
        .filter(e => e.from !== undefined && e.to !== undefined);

    nodeDataSet = new vis.DataSet(nodes);
    edgeDataSet = new vis.DataSet(edges);

    const dataSet = {
        nodes: nodeDataSet,
        edges: edgeDataSet
    };

    const options = {
        layout: {
            improvedLayout: true
        },
        physics: {
            enabled: true,
            solver: "barnesHut",
            barnesHut: {
                gravitationalConstant: -4000,
                centralGravity: 0.1,
                springLength: 150,
                springConstant: 0.04,
                damping: 0.08,
                avoidOverlap: 1
            },
            stabilization: {
                enabled: true,
                iterations: 200,
                updateInterval: 25
            }
        },
        interaction: {
            dragNodes: true,
            dragView: true,
            zoomView: true,
            hover: true,
            selectable: true
        }
    };

    network = new vis.Network(container, dataSet, options);

    network.once("stabilizationIterationsDone", function () {
        network.setOptions({
            physics: {
                enabled: false
            }
        });
    });

    network.on("selectNode", function (params) {
        if (params.nodes.length > 0) {
            handleNodeSelect(params.nodes[0]);
        }
    });

    network.on("deselectNode", function () {
        closeSidebar();
    });
}

function handleNodeSelect(nodeId) {
    const topicName = topicsList[nodeId];
    activeTopic = topicName;

    const data = JSON.parse(localStorage.getItem("data"));
    if (!data) return;

    const sidebar = document.getElementById("detailPanel");
    sidebar.classList.add("active");

    document.getElementById("topicTitle").innerText = topicName;

    // Render links dynamically
    const linksEl = document.getElementById("topicLinks");
    if (linksEl) {
        const webUrl = `https://www.google.com/search?q=${encodeURIComponent(topicName + " tutorial")}`;
        const videoUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(topicName + " explanation")}`;
        const wikiUrl = `https://en.wikipedia.org/wiki/Special:Search?search=${encodeURIComponent(topicName)}`;
        
        linksEl.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 10px;">
                <a href="${webUrl}" target="_blank" style="text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 12px; font-size: 0.95rem; border: 1px solid rgba(56, 189, 248, 0.35); background: rgba(56, 189, 248, 0.1); color: #38bdf8; border-radius: 10px; font-weight: 500; transition: 0.2s; width: 100%; box-sizing: border-box;">
                    🔍 Read Web Tutorial
                </a>
                <a href="${videoUrl}" target="_blank" style="text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 12px; font-size: 0.95rem; border: 1px solid rgba(239, 68, 68, 0.35); background: rgba(239, 68, 68, 0.1); color: #f87171; border-radius: 10px; font-weight: 500; transition: 0.2s; width: 100%; box-sizing: border-box;">
                    📺 Watch YouTube Video
                </a>
                <a href="${wikiUrl}" target="_blank" style="text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 12px; font-size: 0.95rem; border: 1px solid rgba(203, 213, 225, 0.35); background: rgba(203, 213, 225, 0.1); color: #cbd5e1; border-radius: 10px; font-weight: 500; transition: 0.2s; width: 100%; box-sizing: border-box;">
                    📖 View Wikipedia Reference
                </a>
            </div>
        `;
    }

    const expText = document.getElementById("topicExplanation");
    const level = data.level || "advanced";
    const levelLabel = level.charAt(0).toUpperCase() + level.slice(1);
    
    expText.innerHTML = `
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:30px 10px;">
            <div class="spinner"></div>
            <span style="color:#94a3b8; font-size:0.85rem; margin-top:12px;">Querying Cohere for explanation...</span>
        </div>
    `;

    fetch("/api/explain-topic", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            topic: topicName,
            domain: data.domain || "Advanced Studies",
            level: level
        })
    })
    .then(res => res.json())
    .then(resData => {
        if (activeTopic === topicName) {
            expText.innerText = resData.explanation || "No explanation available.";
        }
    })
    .catch(() => {
        if (activeTopic === topicName) {
            expText.innerText = "❌ Error fetching explanation. Please try again.";
        }
    });
}

function closeSidebar() {
    const sidebar = document.getElementById("detailPanel");
    if (sidebar) sidebar.classList.remove("active");
    activeTopic = null;
}