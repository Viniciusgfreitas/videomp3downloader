# Video MP3 Downloader

Uma aplicação web simples e intuitiva de estudo para baixar o áudio de vídeos do YouTube em formato MP3. Basta colar o link do vídeo e clicar em um botão — sem cadastro, sem complicação.

## Funcionalidades

- Interface limpa, responsiva e em português
- Campo único para colar o link do vídeo do YouTube
- Conversão e download do áudio com um clique, via backend próprio (yt-dlp + ffmpeg)
- Mensagens de status para acompanhar o processo
- Ilustração animada em SVG para uma experiência mais agradável

## Tecnologias

| Tecnologia | Uso |
|------------|-----|
| HTML5 | Estrutura da página |
| CSS3 | Estilização e responsividade |
| JavaScript (Vanilla) | Captura do link e chamada ao backend |
| Python 3 (stdlib) | Servidor HTTP do backend |
| yt-dlp | Extração de áudio do YouTube |
| ffmpeg | Conversão do áudio para MP3 |

## Como usar

1. Clone o repositório:
   ```bash
   git clone https://github.com/vinicifreitas/videomp3downloader.git
   cd videomp3downloader
   ```

2. Suba o backend (precisa de Python 3.8+):
   ```bash
   cd backend
   ./setup.sh      # baixa ffmpeg e yt-dlp em backend/bin, se necessário
   python3 server.py
   ```
   O servidor sobe em `http://localhost:8000`. Deixe esse terminal aberto.

3. Em outro terminal, sirva o frontend a partir da raiz do projeto:
   ```bash
   python3 -m http.server 5501
   ```
   (ou use a extensão **Live Server** do VS Code).

4. Abra `http://localhost:5501` no navegador, cole o link do vídeo do YouTube e clique em **Baixar Áudio**.

### Requisitos do backend

- `python3` no PATH.
- `ffmpeg` e `yt-dlp`: se já estiverem instalados no sistema, o backend os usa diretamente. Caso contrário, rode `backend/setup.sh`, que baixa binários autocontidos para `backend/bin/` (não requer root). O yt-dlp muda com frequência para acompanhar o YouTube — se o download começar a falhar com "No video formats found", rode `setup.sh` novamente para atualizar o binário.
- Vídeos com mais de 20 minutos são recusados por padrão (ajustável em `MAX_DURATION_SECONDS` em `backend/server.py`).

## Estrutura do projeto

```
videomp3downloader/
├── index.html          # Página principal
├── style.css           # Estilos da aplicação
├── script.js           # Lógica de download (chama o backend)
├── music-animate.svg   # Ilustração animada
├── backend/
│   ├── server.py        # Servidor HTTP (extrai/converte áudio)
│   ├── setup.sh          # Baixa ffmpeg + yt-dlp autocontidos
│   └── bin/              # (gerado por setup.sh, ignorado no git)
└── README.md
```

## ⚠️ Aviso legal

Este projeto tem fins educacionais. Baixe apenas conteúdos dos quais você possui os direitos ou que estejam sob licença livre. Respeite os Termos de Serviço do YouTube e os direitos autorais dos criadores.

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

---

Desenvolvido por [Vinicius Freitas](https://github.com/vinicifreitas)
