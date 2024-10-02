// document.getElementById('downloadForm').addEventListener('submit', function (e) {
//   e.preventDefault();
  
//   const videoUrl = document.getElementById('videoUrl').value;
//   const statusMessage = document.getElementById('statusMessage');

//   Validação básica
//   if (!videoUrl || !videoUrl.includes("youtube.com")) {
//       statusMessage.textContent = "Por favor, insira um link válido do YouTube.";
//       return;
//   }

//   Exemplo de como você pode trabalhar com um servidor backend (Python, Node.js, etc.)
//   statusMessage.textContent = "Processando o download...";

//   Aqui, você faria uma requisição para o backend para lidar com o download de áudio
//   Exemplo fictício
//   setTimeout(() => {
//       statusMessage.textContent = "Download iniciado!";
//   }, 2000);
// });

const fileInput = document.querySelector("input"),
downloadBtn = document.querySelector("button");

downloadBtn.addEventListener("click", e => {
  e.preventDefault();
  downloadBtn.innerText = "Baixando Áudio";
  fetchFile(fileInput.value);
});

function fetchFile(url) {
  fetch(url).then(res => res.blob()).then(file => {
    let tempUrl = URL.createObjectURL(file);
    let aTag = document.createElement("a");
    aTag.href = tempUrl;
    aTag.download = url.replace(/^.*[\\\/]/, '');
    document.body.appendChild(aTag);
    aTag.click();
    aTag.remove();
    URL.revokeObjectURL(tempUrl);
    downloadBtn.innerText = "Baixar Áudio"
  });
}