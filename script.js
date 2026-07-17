const API_URL = "http://localhost:8000/api/download";

const form = document.getElementById("downloadForm"),
  urlInput = document.getElementById("videoUrl"),
  downloadBtn = document.querySelector("button"),
  statusMessage = document.getElementById("statusMessage");

const YOUTUBE_URL_REGEX = /^https?:\/\/(www\.|m\.|music\.)?(youtube\.com|youtu\.be)\/.+/i;

form.addEventListener("submit", e => {
  e.preventDefault();

  const videoUrl = urlInput.value.trim();

  if (!YOUTUBE_URL_REGEX.test(videoUrl)) {
    statusMessage.textContent = "Por favor, insira um link válido do YouTube.";
    statusMessage.classList.add("error");
    return;
  }

  downloadAudio(videoUrl);
});

async function downloadAudio(url) {
  downloadBtn.disabled = true;
  downloadBtn.innerText = "Baixando Áudio...";
  statusMessage.classList.remove("error");
  statusMessage.textContent = "Processando o download, isso pode levar alguns instantes...";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const { error } = await response.json().catch(() => ({}));
      throw new Error(error || "Não foi possível baixar o áudio.");
    }

    const disposition = response.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="(.+)"/);
    const filename = match ? match[1] : "audio.mp3";

    const blob = await response.blob();
    const tempUrl = URL.createObjectURL(blob);
    const aTag = document.createElement("a");
    aTag.href = tempUrl;
    aTag.download = filename;
    document.body.appendChild(aTag);
    aTag.click();
    aTag.remove();
    URL.revokeObjectURL(tempUrl);

    statusMessage.textContent = "Download concluído!";
  } catch (err) {
    statusMessage.textContent = err.message || "Erro ao baixar o áudio.";
    statusMessage.classList.add("error");
  } finally {
    downloadBtn.disabled = false;
    downloadBtn.innerText = "Baixar Áudio";
  }
}