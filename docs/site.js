AOS.init({
    duration: 700,
    once: true,
    offset: 80,
});

const REPO_URL = "https://github.com/juanzandev/witch-farm-autoclicker";

for (const id of ["repo-link-nav", "repo-link-hero"]) {
    const el = document.getElementById(id);
    if (el) {
        el.href = REPO_URL;
    }
}

const tabButtons = Array.from(document.querySelectorAll("[data-tab-target]"));
const tabPanels = Array.from(document.querySelectorAll("[data-tab-panel]"));
const tabLinks = Array.from(document.querySelectorAll("[data-tab-link]"));

function setActiveTab(tabId) {
    for (const btn of tabButtons) {
        const isActive = btn.dataset.tabTarget === tabId;
        btn.classList.toggle("is-active", isActive);
    }

    for (const panel of tabPanels) {
        const isActive = panel.dataset.tabPanel === tabId;
        panel.classList.toggle("is-active", isActive);
    }

    for (const link of tabLinks) {
        const isActive = link.dataset.tabLink === tabId;
        link.classList.toggle("is-active", isActive);
    }
}

for (const btn of tabButtons) {
    btn.addEventListener("click", () => setActiveTab(btn.dataset.tabTarget));
}

for (const link of tabLinks) {
    link.addEventListener("click", (event) => {
        const tabId = link.dataset.tabLink;
        if (!tabId) {
            return;
        }
        event.preventDefault();
        setActiveTab(tabId);
        const panel = document.querySelector(`[data-tab-panel="${tabId}"]`);
        if (panel) {
            panel.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    });
}

function renderChangelog(entries) {
    const list = document.getElementById("changelog-list");
    if (!list) {
        return;
    }
    if (!Array.isArray(entries) || entries.length === 0) {
        list.innerHTML = '<p class="tiny">No changelog entries yet.</p>';
        return;
    }

    const blocks = entries.map((entry) => {
        const notes = (entry.notes || []).map((item) => `<li>${item}</li>`).join("");
        return `
            <article class="change-entry">
                <div class="change-entry-header">
                    <span class="version-tag">${entry.version || "Unversioned"}</span>
                    <span class="change-date">${entry.date || "Date TBD"}</span>
                </div>
                <h3 class="change-title">${entry.title || "Release Update"}</h3>
                <ul class="change-notes">${notes}</ul>
            </article>
        `;
    });

    list.innerHTML = blocks.join("");
}

async function loadChangelog() {
    try {
        const res = await fetch("changelog.json", { cache: "no-store" });
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        renderChangelog(data);
    } catch (_err) {
        const list = document.getElementById("changelog-list");
        if (list) {
            list.innerHTML = '<p class="tiny">Unable to load changelog right now.</p>';
        }
    }
}

function renderPushFeed(commits) {
    const list = document.getElementById("push-feed");
    if (!list) {
        return;
    }
    if (!Array.isArray(commits) || commits.length === 0) {
        list.innerHTML = '<p class="tiny">No recent pushes found.</p>';
        return;
    }

    const blocks = commits.map((commit) => {
        const sha = (commit.sha || "").slice(0, 7);
        const author = commit.commit?.author?.name || "Unknown";
        const dateRaw = commit.commit?.author?.date;
        const dateText = dateRaw ? new Date(dateRaw).toLocaleString() : "Date unknown";
        const message = (commit.commit?.message || "No commit message").split("\n")[0];
        const url = commit.html_url || REPO_URL;
        return `
            <article class="push-item">
                <div class="push-meta">${sha} • ${author} • ${dateText}</div>
                <p><a class="checksum-link" href="${url}" target="_blank" rel="noopener noreferrer">${message}</a></p>
            </article>
        `;
    });

    list.innerHTML = blocks.join("");
}

async function loadRecentPushes() {
    try {
        const res = await fetch("https://api.github.com/repos/juanzandev/witch-farm-autoclicker/commits?per_page=8", { cache: "no-store" });
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        renderPushFeed(data);
    } catch (_err) {
        const list = document.getElementById("push-feed");
        if (list) {
            list.innerHTML = '<p class="tiny">Could not fetch push history right now.</p>';
        }
    }
}

loadChangelog();
loadRecentPushes();
