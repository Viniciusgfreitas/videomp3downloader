#!/usr/bin/env bash
# Baixa binários auto-contidos (ffmpeg + yt-dlp) para backend/bin quando
# não há acesso root para instalar via apt/pip, ou quando o yt-dlp do
# sistema está desatualizado (o YouTube muda com frequência e uma versão
# antiga do yt-dlp costuma falhar com "No video formats found").
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p bin

# --- ffmpeg ---
if command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg já está disponível no PATH: $(command -v ffmpeg)"
elif [ -x "bin/ffmpeg" ]; then
  echo "ffmpeg estático já presente em backend/bin/ffmpeg"
else
  echo "Baixando build estático do ffmpeg (johnvansickle.com)..."
  tmpdir=$(mktemp -d)
  trap 'rm -rf "$tmpdir"' EXIT

  curl -fL --progress-bar \
    "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz" \
    -o "$tmpdir/ffmpeg.tar.xz"

  tar -xJf "$tmpdir/ffmpeg.tar.xz" -C "$tmpdir"

  extracted_dir=$(find "$tmpdir" -maxdepth 1 -type d -name "ffmpeg-*-amd64-static")
  cp "$extracted_dir/ffmpeg" bin/ffmpeg
  cp "$extracted_dir/ffprobe" bin/ffprobe
  chmod +x bin/ffmpeg bin/ffprobe
  rm -rf "$tmpdir"
  trap - EXIT

  echo "ffmpeg instalado em backend/bin/ffmpeg"
fi

# --- yt-dlp ---
# Sempre busca o binário standalone mais recente: o YouTube muda o
# player/assinatura com frequência e versões antigas quebram rápido.
echo "Baixando yt-dlp standalone mais recente..."
curl -fL --progress-bar \
  "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux" \
  -o bin/yt-dlp
chmod +x bin/yt-dlp
echo "yt-dlp instalado em backend/bin/yt-dlp ($(bin/yt-dlp --version))"
