const $ = (id) => document.getElementById(id);

function today() {
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${mm}-${dd}`;
}

function wordCount(s) {
  const t = s.trim();
  if (!t) return 0;
  return t.split(/\s+/).length;
}

function filenameFromTitle(title) {
  const stem = title.trim().replace(/\s+/g, "_").replace(/[\\/]/g, "");
  return `${stem || "Untitled"}.md`;
}

function composeMarkdown(title, date, body) {
  const escaped = title.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  return `---\ntitle: "${escaped}"\ndate: ${date}\n---\n\n${body.replace(/^\n+/, "")}`;
}

function setStatus(msg) {
  $("status").textContent = msg || "";
}

function saveDraft() {
  localStorage.setItem("blargl", JSON.stringify({
    title: $("title").value,
    date: $("date").value,
    body: $("input").value,
  }));
}

function loadDraft() {
  try {
    const draft = JSON.parse(localStorage.getItem("blargl") || "null");
    if (!draft) return;
    $("title").value = draft.title || "";
    $("date").value = draft.date || today();
    $("input").value = draft.body || "";
  } catch {
    /* ignore a corrupt draft */
  }
}

function render() {
  const body = $("input").value;
  $("output").innerHTML = marked.parse(body, { gfm: true, breaks: false });
  $("wordcount").textContent = String(wordCount(body));
  saveDraft();
}

function download(filename, text) {
  const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function savePost() {
  const title = $("title").value.trim();
  const date = $("date").value || today();
  const body = $("input").value;
  if (!title) {
    $("title").focus();
    setStatus("Add a title first.");
    return;
  }

  const filename = filenameFromTitle(title);
  const markdown = composeMarkdown(title, date, body);
  setStatus("Saving…");

  try {
    const res = await fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, date, body, filename, markdown }),
    });
    if (res.ok) {
      const data = await res.json();
      setStatus(`Saved ${data.path}. Open ${data.url}`);
      return;
    }
  } catch {
    /* not running serve.py — fall through to download */
  }

  download(filename, markdown);
  setStatus(`Downloaded ${filename}. Put it in posts/ and run python3 publish.py`);
}

function init() {
  if (!$("date").value) $("date").value = today();
  loadDraft();
  if (!$("date").value) $("date").value = today();
  render();

  $("input").addEventListener("input", render);
  $("title").addEventListener("input", saveDraft);
  $("date").addEventListener("input", saveDraft);
  $("save").addEventListener("click", savePost);

  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "s") {
      event.preventDefault();
      savePost();
    }
  });
}

init();
