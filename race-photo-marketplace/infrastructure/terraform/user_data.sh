#!/bin/bash
yum update -y
yum install -y python3 python3-pip git

# Instalar Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Clonar repositório (substitua pela URL do seu repo)
cd /home/ec2-user
git clone https://github.com/seu-usuario/race-photo-marketplace.git
cd race-photo-marketplace

# Instalar dependências
pip3 install -r requirements.txt

# Inicializar banco
python3 src/app.py init-db

# Criar serviço systemd
cat > /etc/systemd/system/race-photos.service << EOF
[Unit]
Description=Race Photos Marketplace
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/race-photo-marketplace
ExecStart=/usr/bin/python3 src/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable race-photos
systemctl start race-photos