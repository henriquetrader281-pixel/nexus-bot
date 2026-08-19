const DEFAULT_AFFILIATE_ID = "18316451024";

const state = {
  tab: null,
  page: null,
  items: [],
};

const $ = (selector) => document.querySelector(selector);

function setStatus(message, kind = "info") {
  const status = $("#status");
  status.textContent = message;
  status.dataset.kind = kind;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function fileNameFor(item, index) {
  const fallback = `${item.type === "video" ? "nexus-video" : "nexus-imagem"}-${index + 1}`;
  try {
    const url = new URL(item.url);
    const raw = decodeURIComponent(url.pathname.split("/").pop() || "");
    const cleaned = raw.replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^-+|-+$/g, "");
    if (cleaned) return cleaned;
  } catch {
    // Usa o nome de fallback quando o recurso não tem uma URL convencional.
  }
  return `${fallback}.${item.type === "video" ? "mp4" : "jpg"}`;
}

function downloadItem(item, index, saveAs = true) {
  chrome.downloads.download(
    {
      url: item.url,
      filename: `Nexus/${fileNameFor(item, index)}`,
      saveAs,
      conflictAction: "uniquify",
    },
    (downloadId) => {
      if (chrome.runtime.lastError || !downloadId) {
        setStatus(chrome.runtime.lastError?.message || "Não foi possível iniciar o download.", "error");
        return;
      }
      setStatus("Download iniciado.", "success");
    },
  );
}

function selectedItems() {
  return state.items.filter((item) => item.selected);
}

function renderItems() {
  const list = $("#media-list");
  const count = $("#media-count");
  count.textContent = `${state.items.length} recurso${state.items.length === 1 ? "" : "s"}`;

  if (!state.items.length) {
    list.innerHTML = '<div class="empty">Nenhuma imagem ou vídeo público foi encontrado nesta página.</div>';
    return;
  }

  list.innerHTML = state.items
    .map((item, index) => {
      const preview = item.type === "video"
        ? `<video src="${escapeHtml(item.url)}" muted preload="metadata"></video>`
        : `<img src="${escapeHtml(item.url)}" alt="Pré-visualização do recurso ${index + 1}" loading="lazy">`;
      return `
        <article class="media-item" data-index="${index}">
          <label class="media-check">
            <input type="checkbox" data-select="${index}" ${item.selected ? "checked" : ""}>
            <span class="preview">${preview}</span>
            <span class="media-meta">
              <strong><span class="badge ${item.type}">${item.type === "video" ? "VÍDEO" : "IMAGEM"}</span> ${escapeHtml(item.source)}</strong>
              <small title="${escapeHtml(item.url)}">${escapeHtml(item.url)}</small>
            </span>
          </label>
          <button class="icon-button" data-download="${index}" title="Descarregar este recurso">↓</button>
        </article>
      `;
    })
    .join("");

  list.querySelectorAll("[data-select]").forEach((input) => {
    input.addEventListener("change", (event) => {
      const index = Number(event.currentTarget.dataset.select);
      state.items[index].selected = event.currentTarget.checked;
      updateSelectionSummary();
    });
  });

  list.querySelectorAll("[data-download]").forEach((button) => {
    button.addEventListener("click", () => {
      const index = Number(button.dataset.download);
      downloadItem(state.items[index], index);
    });
  });

  updateSelectionSummary();
}

function updateSelectionSummary() {
  const total = selectedItems().length;
  $("#selection-count").textContent = `${total} selecionado${total === 1 ? "" : "s"}`;
  $("#download-selected").disabled = total === 0;
  $("#export-nexus").disabled = total === 0;
}

async function getActiveTab() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tabs[0]?.id) throw new Error("Não foi possível identificar a aba ativa.");
  return tabs[0];
}

async function scanPage() {
  setStatus("A analisar a página…");
  $("#refresh").disabled = true;
  try {
    state.tab = await getActiveTab();
    const [result] = await chrome.scripting.executeScript({
      target: { tabId: state.tab.id },
      func: collectMediaFromPage,
    });
    state.page = result?.result || { title: "Página sem título", url: state.tab.url || "", items: [] };
    state.items = (state.page.items || []).map((item) => ({ ...item, selected: true }));
    $("#page-title").textContent = state.page.title || "Página atual";
    $("#page-url").textContent = state.page.url || state.tab.url || "";
    renderItems();
    setStatus(state.items.length ? "Recursos encontrados." : "A página não expôs recursos públicos detetáveis.", state.items.length ? "success" : "info");
  } catch (error) {
    state.items = [];
    renderItems();
    setStatus(`Não foi possível analisar esta página: ${error.message}`, "error");
  } finally {
    $("#refresh").disabled = false;
  }
}

async function downloadSelected() {
  const items = selectedItems();
  if (!items.length) return;
  items.forEach((item) => downloadItem(item, state.items.indexOf(item), false));
  setStatus(`${items.length} download${items.length === 1 ? "" : "s"} iniciado${items.length === 1 ? "" : "s"}.`, "success");
}

async function exportToNexus() {
  const items = selectedItems();
  if (!items.length) return;
  const images = items.filter((item) => item.type === "image");
  const videos = items.filter((item) => item.type === "video");
  const payload = {
    product_name: state.page?.title || "Produto selecionado",
    product_source_url: state.page?.url || state.tab?.url || "",
    image_url: images[0]?.url || null,
    source_image_url: images[0]?.url || null,
    video_source_url: videos[0]?.url || null,
    media: items.map(({ type, url, source }) => ({ type, url, source })),
    source: "browser_extension",
    extracted_at: new Date().toISOString(),
  };
  await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
  setStatus("Dados copiados. Cole-os no fluxo de campanha do Nexus.", "success");
}

async function copyAffiliateLink() {
  const rawUrl = state.page?.url || state.tab?.url || "";
  if (!rawUrl) return;
  const affiliateId = $("#affiliate-id").value.trim() || DEFAULT_AFFILIATE_ID;
  try {
    const url = new URL(rawUrl);
    url.search = "";
    url.hash = "";
    url.searchParams.set("smtt", `0.0.${affiliateId}`);
    await navigator.clipboard.writeText(url.toString());
    setStatus("Link de afiliado copiado.", "success");
  } catch {
    setStatus("A URL atual não é válida para gerar o link.", "error");
  }
}

function collectMediaFromPage() {
  const pageUrl = window.location.href;
  const pageTitle = document.title || "Página atual";
  const found = [];
  const seen = new Set();
  const imagePattern = /\.(?:jpe?g|png|webp|gif|avif|bmp)(?:[?#].*)?$/i;
  const videoPattern = /\.(?:mp4|webm|mov|m4v|m3u8)(?:[?#].*)?$/i;

  const normalise = (value) => {
    if (!value || typeof value !== "string") return null;
    const cleaned = value
      .replaceAll("\\/", "/")
      .replaceAll("\\u002F", "/")
      .replaceAll("&amp;", "&")
      .trim();
    if (!cleaned || cleaned.startsWith("data:") || cleaned.startsWith("blob:") || cleaned.startsWith("javascript:")) return null;
    try {
      const url = new URL(cleaned, pageUrl).href;
      if (!/^https?:$/i.test(new URL(url).protocol)) return null;
      return url;
    } catch {
      return null;
    }
  };

  const add = (value, type, source) => {
    const url = normalise(value);
    if (!url || seen.has(url)) return;
    seen.add(url);
    found.push({ url, type, source });
  };

  const fromSrcset = (value) => {
    if (!value) return;
    String(value).split(",").forEach((part) => add(part.trim().split(/\s+/)[0], "image", "srcset"));
  };

  document.querySelectorAll("img").forEach((element) => {
    fromSrcset(element.getAttribute("srcset"));
    ["src", "data-src", "data-original", "data-lazy-src", "data-image", "data-url"].forEach((attribute) => {
      add(element.getAttribute(attribute), "image", `img[${attribute}]`);
    });
    add(element.currentSrc, "image", "img.currentSrc");
  });

  document.querySelectorAll("video").forEach((element) => {
    add(element.currentSrc, "video", "video.currentSrc");
    add(element.getAttribute("src"), "video", "video[src]");
    add(element.getAttribute("poster"), "image", "video[poster]");
  });

  document.querySelectorAll("source").forEach((element) => {
    const value = element.getAttribute("src") || element.getAttribute("srcset");
    const type = /video/i.test(element.getAttribute("type") || "") || videoPattern.test(value || "") ? "video" : "image";
    if (value?.includes(",")) {
      value.split(",").forEach((part) => add(part.trim().split(/\s+/)[0], type, "source[srcset]"));
    } else {
      add(value, type, "source[src]");
    }
  });

  // Muitos players não deixam o MP4 no DOM: carregam-no via fetch/XHR,
  // atribuem um blob: ao elemento video ou usam um manifesto HLS/DASH.
  // A Performance Resource Timeline mantém o URL HTTP original em vários
  // destes casos, mesmo quando video.currentSrc é apenas blob:.
  if (typeof performance?.getEntriesByType === "function") {
    performance.getEntriesByType("resource").forEach((entry) => {
      const resourceUrl = entry.name || "";
      const initiator = String(entry.initiatorType || "").toLowerCase();
      const mediaByExtension = videoPattern.test(resourceUrl) || /\.(?:mpd|m3u8)(?:[?#].*)?$/i.test(resourceUrl);
      const mediaByInitiator = /^(?:video|audio|media)$/.test(initiator);
      const mediaByNetworkHint = /^(?:fetch|xmlhttprequest|other)$/.test(initiator)
        && /(?:video|media|stream|playback|manifest|hls|dash|mp4|webm|m3u8)/i.test(resourceUrl);
      if (mediaByExtension || mediaByInitiator || mediaByNetworkHint) {
        add(resourceUrl, "video", `performance:${initiator || "resource"}`);
      }
    });
  }

  document.querySelectorAll("meta[property], meta[name]").forEach((element) => {
    const key = `${element.getAttribute("property") || ""} ${element.getAttribute("name") || ""}`.toLowerCase();
    const value = element.getAttribute("content");
    if (key.includes("image")) add(value, "image", "meta");
    if (key.includes("video") || key.includes("content_url")) add(value, "video", "meta");
  });

  document.querySelectorAll("link[rel]").forEach((element) => {
    const rel = (element.getAttribute("rel") || "").toLowerCase();
    if (rel.includes("image")) add(element.getAttribute("href"), "image", "link");
    if (rel.includes("video") || rel.includes("preload")) {
      const value = element.getAttribute("href");
      add(value, videoPattern.test(value || "") ? "video" : "image", "link");
    }
  });

  document.querySelectorAll("a[href]").forEach((element) => {
    const href = element.getAttribute("href") || "";
    if (videoPattern.test(href)) add(href, "video", "link[href]");
    if (imagePattern.test(href)) add(href, "image", "link[href]");
  });

  document.querySelectorAll("*").forEach((element) => {
    const background = getComputedStyle(element).backgroundImage || "";
    const matches = background.matchAll(/url\(["']?([^"')]+)["']?\)/g);
    for (const match of matches) add(match[1], "image", "background-image");
  });

  const html = document.documentElement?.innerHTML || "";
  const escapedUrls = html.match(/https?:\\?\/\\?\/[^"'\s<>]+/g) || [];
  escapedUrls.forEach((value) => {
    const clean = value.replaceAll("\\/", "/");
    if (videoPattern.test(clean)) add(clean, "video", "código da página");
    if (imagePattern.test(clean)) add(clean, "image", "código da página");
  });

  return {
    title: pageTitle,
    url: pageUrl,
    items: found.slice(0, 200),
  };
}

$("#refresh").addEventListener("click", scanPage);
$("#download-selected").addEventListener("click", downloadSelected);
$("#export-nexus").addEventListener("click", exportToNexus);
$("#copy-affiliate").addEventListener("click", copyAffiliateLink);
$("#select-all").addEventListener("click", () => {
  state.items.forEach((item) => { item.selected = true; });
  renderItems();
});
$("#clear-all").addEventListener("click", () => {
  state.items.forEach((item) => { item.selected = false; });
  renderItems();
});

scanPage();
