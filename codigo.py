#Importando sistemas
import pygame
import sys
import random
import os

#Inicializando sistemas
pygame.init()
pygame.mixer.init()
pygame.font.init()

#Configurações de janela
largura = 800 #tamanho da largura
altura = 600 #tamanho da altura
janela = "Jogo da Cobrinha" #nome da janela

pygame.display.set_caption(janela)
tela = pygame.display.set_mode((largura, altura))

#Gerenciando a taxa de FPS
relogio = pygame.time.Clock()

#Fonte para textos na tela
fonte_game = pygame.font.SysFont("Times New Roman", 30, bold=True)
fonte_game_2 = pygame.font.SysFont("Times New Roman", 30, bold=True)

#Cores (RGB)
fundo = (40, 60, 48) #Verde para o fundo
cabeca = (106, 192, 76) #Verde da cabeça
corpo = (106, 192, 76) #Verde do corpo
maca = (192, 76, 76) #Vermelho da maçã
bomba = (0, 0, 0) #Preto
texto = (254, 255, 253) #Branco (suave)

cores_cobrinha = [
    (106, 192, 76), #Verde escuro
    (156, 236, 124), #Verde claro
    (192, 76, 76), #Vermelho
    (254, 255, 253), #Branco (suave)
    (0, 0, 0) #Preto
]

#Fases
fases = {
    1: {"fps": 6, "chance_bomba": 0.20, "tempo_item": 6000, "meta_pontuacao": 100}, #fase 1
    2: {"fps": 8, "chance_bomba": 0.40, "tempo_item": 5000, "meta_pontuacao": 200}, #fase 2
    3: {"fps": 10, "chance_bomba": 0.60, "tempo_item": 4500, "meta_pontuacao": None} #fase 3
}

fase_maxima = max(fases.keys())

#Pontuação, vidas e métricas
pontuacao = 0
vidas = 3
fase_atual = 1

tamanho_personagem = 50
velocidade = tamanho_personagem

pos_x = 0
pos_y = 0
dir_x = 0
dir_y = 0

corpo_cobra = []
cobra_viva = True

tela_inicial = True

#Sprites
sprites = {}
usar_sprites = True
pasta_imagens = "Imagens"

arquivo_sprites = {
    "cabeça": "cabeca.png", #cabeça da cobra
    "morta": "morte.png", #cabeça da cobra morta
    "corpo": "corpo.png", #corpo da cobra
    "maçã vermelha": "maca.png", #maçã vermelha
    "maçã verde": "maca_verde.png", #maçã verde
    "bomba": "bomba.png" #bomba
}

#Carregando os sprites
print("[INFO] Carregando sprites...")
for chave, arquivo in arquivo_sprites.items():
    caminho = os.path.join(pasta_imagens, arquivo)
    try:
        img = pygame.image.load(caminho).convert_alpha()
        sprites[chave] = pygame.transform.scale(img, (tamanho_personagem, tamanho_personagem))
    except (FileNotFoundError, pygame.error):
        print(f"[AVISO] Falha ao carregar '{caminho}'. Fallback geométrico ativado para {chave}.")
        usar_sprites = False

#Sons

som_morte = None
pasta_sons = "sons"

#Carregando o som de morte
try:
    caminho_som = os.path.join(pasta_sons, "morreu.mp3")
    som_morte = pygame.mixer.Sound(caminho_som)
    print("[INFO] Efeito sonoro 'morreu.mp3' carregado com sucesso!")
except (FileNotFoundError, pygame.error):
    print(f"[AVISO] Arquivo de som 'morreu.mp3' não encontrado. O jogo rodará em modo silencioso.")

som_bomba = None
pasta_sons = "sons"

#Carregando o som de morte por bomba
try:
    caminho_som = os.path.join(pasta_sons, "morte_bomba.mp3")
    som_bomba = pygame.mixer.Sound(caminho_som)
    print("[INFO] Efeito sonoro 'morte_bomba.mp3' carregado com sucesso!")
except (FileNotFoundError, pygame.error):
    print(f"[AVISO] Arquivo de som 'morte_bomba.mp3' não encontrado. O jogo rodará em modo silencioso.")

som_comida = None
pasta_sons = "sons"

#Carregando o som de comida
try:
    caminho_som = os.path.join(pasta_sons, "comendo.mp3")
    som_comida = pygame.mixer.Sound(caminho_som)
    print("[INFO] Efeito sonoro 'comendo.mp3' carregado com sucesso!")
except (FileNotFoundError, pygame.error):
    print(f"[AVISO] Arquivo de som 'comendo.mp3' não encontrado. O jogo rodará em modo silencioso.")

som_nova_fase = None
pasta_sons = "sons"

#Carregando o som de próxima fase
try:
    caminho_som = os.path.join(pasta_sons, "ebaa.mp3")
    som_nova_fase = pygame.mixer.Sound(caminho_som)
    print("[INFO] Efeito sonoro 'ebaa.mp3' carregado com sucesso!")
except (FileNotFoundError, pygame.error):
    print(f"[AVISO] Arquivo de som 'ebaa.mp3' não encontrado. O jogo rodará em modo silencioso.")

#Gerenciando itens que serão gerados
momento_geracao = 0
pos_fruta = None
tipo_fruta = None
pos_bomba = None
bomba_ativa = False

#Definindo a função para gerar uma posição aleatória na tela
def gerar_posicao_aleatoria():
    colunas = largura // tamanho_personagem
    linhas = altura // tamanho_personagem
    while True:
        x = random.randint(0, colunas - 1) * tamanho_personagem
        y = random.randint(0, linhas - 1) * tamanho_personagem
        if [x, y] not in corpo_cobra:
            return x, y

#Definindo a função para spawnar itens na tela
def spawnar_itens():
    global pos_fruta, tipo_fruta, pos_bomba, bomba_ativa, momento_geracao
    momento_geracao = pygame.time.get_ticks()
    chance_bomba = fases[fase_atual]["chance_bomba"]

    if random.random() < chance_bomba:
        pos_bomba = gerar_posicao_aleatoria()
        bomba_ativa = True
        if random.random() < 0.50:
            pos_fruta = gerar_posicao_aleatoria()
            tipo_fruta = random.choice(["vermelha", "verde"])
        else:
            pos_fruta = None
            tipo_fruta = None
    else:
        pos_fruta = gerar_posicao_aleatoria()
        tipo_fruta = random.choice(["vermelha", "verde"])
        pos_bomba = None
        bomba_ativa = False

#Fluxo do jogo
#Definindo a função para reiniciar a posição da cobra
def reiniciar_posicao_da_cobra():
    global pos_x, pos_y, dir_x, dir_y, corpo_cobra, cobra_viva
    pos_x = (largura // 2) // tamanho_personagem * tamanho_personagem
    pos_y = (altura // 2) // tamanho_personagem * tamanho_personagem
    dir_x = velocidade
    dir_y = 0
    corpo_cobra = [
        [pos_x, pos_y],
        [pos_x - tamanho_personagem, pos_y],
        [pos_x - (2 * tamanho_personagem), pos_y]
    ]
    cobra_viva = True

#Definindo a função da morte por colisão
def morte_por_colisao(motivo):
    global vidas
    vidas -= 1
    print(f"[MORTE] Motivo: {motivo} Vidas restantes: {vidas}")
    if som_morte:
        som_morte.play()
    if vidas > 0:
        reiniciar_posicao_da_cobra()
        spawnar_itens()

#Definindo a função da morte por bomba
def morte_por_bomba():
    global pontuacao, vidas
    vidas -= 1
    pontuacao = max(0, pontuacao - 100)
    print(f"[MORTE] Motivo: Atingiu uma bomba! Vidas restantes: {vidas}")
    if som_bomba:
        som_bomba.play()
    if vidas > 0:
        reiniciar_posicao_da_cobra()
        spawnar_itens()

#Laço principal do jogo (game loop)
reiniciar_posicao_da_cobra()
spawnar_itens()

rodando = True
while rodando:
    tempo_atual = pygame.time.get_ticks()
    configuracoes_fase_atual = fases[fase_atual]
    tempo_limite_itens = configuracoes_fase_atual["tempo_item"]

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            if tela_inicial:
                tela_inicial = False
                reiniciar_posicao_da_cobra()
                spawnar_itens()
                continue

            if vidas <= 0:
                if evento.key == pygame.K_r:
                    pontuacao = 0
                    vidas = 3
                    fase_atual = 1
                    reiniciar_posicao_da_cobra()
                    spawnar_itens()
                continue

            #Setinhas e WASD para locomoção da cobrinha
            if evento.key in [pygame.K_LEFT, pygame.K_a] and dir_x == 0:
                dir_x = -velocidade;
                dir_y = 0
            elif evento.key in [pygame.K_RIGHT, pygame.K_d] and dir_x == 0:
                dir_x = velocidade;
                dir_y = 0
            elif evento.key in [pygame.K_UP, pygame.K_w] and dir_y == 0:
                dir_x = 0;
                dir_y = -velocidade
            elif evento.key in [pygame.K_DOWN, pygame.K_s] and dir_y == 0:
                dir_x = 0;
                dir_y = velocidade

# Lógica de atualização
    if vidas > 0 and not tela_inicial:
        if tempo_atual - momento_geracao > tempo_limite_itens:
            spawnar_itens()

        proximo_x = pos_x + dir_x
        proximo_y = pos_y + dir_y

        if proximo_x < 0 or proximo_x > largura - tamanho_personagem or proximo_y < 0 or proximo_y > altura - tamanho_personagem:
            morte_por_colisao("Colisão com a parede!")
            continue

        nova_cabeca = [proximo_x, proximo_y]

        if nova_cabeca in corpo_cobra:
            morte_por_colisao("Colisão com o próprio corpo!")
            continue

        colidiu_com_bomba = False
        if bomba_ativa:
            if nova_cabeca == list(pos_bomba):
                colidiu_com_bomba = True
            else:
                for parte in corpo_cobra:
                    if parte == list(pos_bomba):
                        colidiu_com_bomba = True
                        break

        if colidiu_com_bomba:
            morte_por_bomba()
            continue

        pos_x = proximo_x
        pos_y = proximo_y
        corpo_cobra.insert(0, nova_cabeca)

        comeu_fruta = False
        if pos_fruta and nova_cabeca == list(pos_fruta):
            comeu_fruta = True

        if comeu_fruta:
            pontuacao += 10
            spawnar_itens()
            if som_comida:
                som_comida.play()
        else:
            corpo_cobra.pop()

        if fase_atual < fase_maxima:
            meta_pontuacao_fase = fases[fase_atual]["meta_pontuacao"]

            if pontuacao >= meta_pontuacao_fase:
                fase_atual += 1
                if som_nova_fase:
                    som_nova_fase.play()
                spawnar_itens()

# Renderização gráfica
    tela.fill(fundo)

    if tela_inicial:
        tela.fill(fundo)

        sup_titulo = fonte_game.render("JOGO DA COBRINHA :D", True, texto) #tela de início
        sup_iniciar = fonte_game.render("Pressione qualquer tecla para iniciar", True, texto)

        tela.blit(sup_titulo, sup_titulo.get_rect(center=(largura // 2, altura // 2 - 40)))
        tela.blit(sup_iniciar, sup_iniciar.get_rect(center=(largura // 2, altura // 2 + 20)))

        pygame.display.flip()
        relogio.tick(60)
        continue

    if pos_fruta:
        if usar_sprites:
            sprite_maca = sprites["maçã vermelha"] if tipo_fruta == "vermelha" else sprites["maçã verde"]
            tela.blit(sprite_maca, pos_fruta)
        else:
            pygame.draw.rect(tela, maca,
                             (pos_fruta[0] + 5, pos_fruta[1] + 5, tamanho_personagem - 10, tamanho_personagem - 10))

    if bomba_ativa and pos_bomba:
        if usar_sprites:
            tela.blit(sprites["bomba"], pos_bomba)
        else:
            pygame.draw.rect(tela, bomba,
                             (pos_bomba[0] + 5, pos_bomba[1] + 5, tamanho_personagem - 10, tamanho_personagem - 10))

    for indice, parte in enumerate(corpo_cobra):
        if indice == 0:
            if usar_sprites:
                sprite_cabeca = sprites["cabeça"] if vidas > 0 else sprites["morta"]
                tela.blit(sprite_cabeca, (parte[0], parte[1]))
            else:
                cor_cabeca_atual = cabeca if vidas > 0 else (106, 192, 76)
                pygame.draw.rect(tela, cor_cabeca_atual, (parte[0], parte[1], tamanho_personagem, tamanho_personagem))
        else:
            if usar_sprites:
                tela.blit(sprites["corpo"], (parte[0], parte[1]))
            else:
                pygame.draw.rect(tela, corpo, (parte[0] + 2, parte[1] + 2, tamanho_personagem - 4, tamanho_personagem - 4))

#Placar das informações
    texto_pontuacao = f"PONTUAÇÃO: {pontuacao}"
    texto_vidas = f"VIDAS: {vidas}"
    texto_fase = f"FASE: {fase_atual}" if fase_atual < 3 else "FASE: FINAL (3)"

    if vidas <= 0:
        sup_game_over = fonte_game.render("GAME OVER! :(", True, bomba) #tela de game over
        sup_pontuacao_final = fonte_game.render(f"Sua pontuação foi: {pontuacao}", True, bomba)
        sup_reiniciar = fonte_game.render("Pressione R para reiniciar", True, bomba)

        tela.blit(sup_game_over, sup_game_over.get_rect(center=(largura // 2, altura // 2 - 40)))
        tela.blit(sup_pontuacao_final, sup_pontuacao_final.get_rect(center=(largura // 2, altura // 2)))
        tela.blit(sup_reiniciar, sup_reiniciar.get_rect(center=(largura // 2, altura // 2 + 40)))

    sup_pontuacao = fonte_game.render(texto_pontuacao, True, texto)
    sup_vidas = fonte_game.render(texto_vidas, True, texto)
    sup_fase = fonte_game.render(texto_fase, True, texto)

    tela.blit(sup_pontuacao, sup_pontuacao.get_rect(topright=(largura - 20, 20)))
    tela.blit(sup_vidas, sup_vidas.get_rect(topright=(largura - 20, 50)))
    tela.blit(sup_fase, sup_fase.get_rect(topright=(largura - 20, 80)))

    pygame.display.flip()
    relogio.tick(configuracoes_fase_atual["fps"])

#Finalização do jogo
pygame.quit()
sys.exit()
