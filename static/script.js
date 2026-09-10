async function generate() {
    const text = document.getElementById("inputText").value;
    const status = document.getElementById("status");

    if (!text.trim()) {
        status.innerText = "⚠️ Please enter some text first.";
        status.style.color = "#f59e0b";
        return;
    }

    status.innerText = "⏳ Generating learning graph...";
    status.style.color = "#60a5fa";

    const btn = document.getElementById("generateBtn");
    if (btn) btn.disabled = true;

    try {
        const res = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        const data = await res.json();

        localStorage.setItem("data", JSON.stringify(data));

        status.innerText = "✅ Generated! Redirecting...";
        status.style.color = "#22c55e";

        setTimeout(() => {
            window.location.href = "/dashboard";
        }, 600);

    } catch (err) {
        console.error(err);
        status.innerText = "❌ Error generating graph.";
        status.style.color = "#ef4444";

        if (btn) btn.disabled = false;
    }
}


/* ================= DASHBOARD LOADER ================= */

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

function renderDashboard() {
    const data = JSON.parse(localStorage.getItem("data"));
    if (!data) return;

    // Set domain name
    const domainEl = document.getElementById("domain");
    if (domainEl) domainEl.innerText = data.domain || "Custom Curriculum";

    // Set level badge
    const badgeContainer = document.getElementById("levelBadgeContainer");
    if (badgeContainer) {
        const level = data.level || "advanced";
        let badgeClass = "badge-locked";
        let label = "Advanced";
        if (level === "beginner") {
            badgeClass = "badge-ready";
            label = "🌱 Beginner";
        } else if (level === "intermediate") {
            badgeClass = "badge-completed";
            label = "⚙️ Intermediate";
        } else {
            badgeClass = "badge-locked";
            label = "Advanced";
        }
        badgeContainer.innerHTML = `<span class="badge ${badgeClass}" style="font-size:0.9rem; padding: 6px 12px;">${label}</span>`;
    }

    const allTopics = data.graph.topics || [];
    const prereqs = getPrerequisitesMap(data.graph);

    // Render Full Learning Path (in topological order)
    const lpList = document.getElementById("learning_path");
    if (lpList) {
        lpList.innerHTML = "";
        allTopics.forEach((t, i) => {
            const li = document.createElement("li");
            li.className = "list-item ready";
            li.style.display = "flex";
            li.style.justifyContent = "space-between";
            li.style.alignItems = "center";
            li.style.padding = "12px 16px";

            const webUrl = `https://www.google.com/search?q=${encodeURIComponent(t + " tutorial")}`;
            const videoUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(t + " explanation")}`;

            li.innerHTML = `
                <div class="item-label">
                    <span class="index">${i + 1}.</span>
                    <span class="topic-name" style="font-weight: 500;">${t}</span>
                </div>
                <div class="learning-links" style="display: flex; gap: 8px;">
                    <a href="${webUrl}" target="_blank" style="text-decoration: none; display: flex; align-items: center; gap: 4px; padding: 6px 12px; font-size: 0.8rem; border: 1px solid rgba(56, 189, 248, 0.35); background: rgba(56, 189, 248, 0.1); color: #38bdf8; border-radius: 8px; font-weight: 500; transition: 0.2s;">
                        🔍 Web Tutorial
                    </a>
                    <a href="${videoUrl}" target="_blank" style="text-decoration: none; display: flex; align-items: center; gap: 4px; padding: 6px 12px; font-size: 0.8rem; border: 1px solid rgba(239, 68, 68, 0.35); background: rgba(239, 68, 68, 0.1); color: #f87171; border-radius: 8px; font-weight: 500; transition: 0.2s;">
                        📺 YouTube Video
                    </a>
                </div>
            `;
            lpList.appendChild(li);
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const data = JSON.parse(localStorage.getItem("data"));
    if (data) {
        renderDashboard();
    }
});