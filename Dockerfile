FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive

# 1) Dependencias sistema
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates libnss3 libasound2 libxss1 \
    fonts-liberation libappindicator3-1 lsb-release xdg-utils \
  && rm -rf /var/lib/apt/lists/*

# 2) Instalar Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
     > /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update && apt-get install -y google-chrome-stable \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3) Dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copiar todo el proyecto
COPY . .

# 5) Hacer ejecutable
RUN chmod +x run_all.sh

# 6) Arrancar ambos scripts
CMD ["./run_all.sh"]