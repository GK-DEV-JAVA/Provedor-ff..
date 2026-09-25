import discord
from discord.ext import commands
import os
import random
import threading
import requests
from flask import Flask, jsonify

TOKEN = os.getenv("DISCORD_TOKEN")
CARGO_ID = 1552902262496436275

# CONFIG DO PROVEDOR FF - TROCA AQUI
API_PROVEDOR_FF = "https://sua-api-aqui.com/criar"
API_KEY_FF = "sua-key-aqui"

app = Flask(__name__)
salas = {}
id_atual = 100000

@app.route('/')
def home(): return "GK SALAS FF 24H", 200
@app.route('/health')
def health(): return jsonify({"status":"online"}), 200

def run_api():
    from waitress import serve
    port = int(os.environ.get("PORT", 8000))
    serve(app, host="0.0.0.0", port=port)

def criar_sala_no_provedor(nome, senha):
    try:
        payload = {"nome": nome, "senha": senha, "key": API_KEY_FF}
        r = requests.post(API_PROVEDOR_FF, json=payload, timeout=15)
        print(f"Provedor retorno: {r.text}")
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"Erro provedor: {e}")
        return None

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ ONLINE: {bot.user}")

@bot.command(name="criar")
async def criar(ctx, nome=None, senha=None):
    global id_atual
    id_atual += 1
    if not nome: nome = f"SALA-{ctx.author.name}"
    if not senha: senha = str(random.randint(100,999))
    
    # Cria no provedor FF
    provedor = criar_sala_no_provedor(nome, senha)
    
    salas[id_atual] = {"id":id_atual, "nome":nome, "senha":senha, "dono":ctx.author.id}
    
    embed = discord.Embed(title=f"✅ SALA FF #{id_atual} CRIADA", color=0x2ECC71)
    embed.add_field(name="🆔 ID", value=f"```{id_atual}```", inline=True)
    embed.add_field(name="🔑 Senha", value=f"`{senha}`", inline=True)
    embed.add_field(name="📋 Nome", value=nome, inline=False)
    if provedor:
        embed.add_field(name="Provedor", value="✅ Criada no FF", inline=False)
    else:
        embed.add_field(name="Provedor", value="⚠️ Criada só no bot (API off)", inline=False)
    
    await ctx.send(embed=embed, content=f"{ctx.author.mention}")

@bot.command(name="fechar")
async def fechar(ctx, id_sala:int):
    if id_sala in salas:
        del salas[id_sala]
        await ctx.send(f"🔒 Sala {id_sala} fechada!")
    else:
        await ctx.send("ID não encontrado")

threading.Thread(target=run_api, daemon=True).start()
bot.run(TOKEN)
