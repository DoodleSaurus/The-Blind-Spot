import subprocess
import sys
import pkg_resources
import os
import time
import random

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def matrix_rain():
    """Breve animazione Matrix rain"""
    chars = "010101010111100001111000011110000111100001111000011110000111101010101011110000111100001111000011110000111100001111000011110101010101111000011110000111100001111000011110000111100001111"
    for _ in range(20):
        line = ''.join(random.choice(chars) for _ in range(40))
        print(f"\033[92m{line}\033[0m")
        time.sleep(0.1)
    print()

def loading_spinner(duration=2):
    """Animazione spinner di caricamento"""
    spinners = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r\033[96m{spinners[i % len(spinners)]} Caricamento in corso...\033[0m", end='', flush=True)
        time.sleep(0.1)
        i += 1
    print("\r" + " " * 50 + "\r", end='')

def glitch_text(text, glitches=3):
    """Effetto glitch sul testo"""
    glitch_chars = "!<>-_\\/[]{}—=+*^?#________"
    for _ in range(glitches):
        glitched = ''.join(random.choice(glitch_chars) if random.random() < 0.3 else c for c in text)
        print(f"\r\033[95m{glitched}\033[0m", end='', flush=True)
        time.sleep(0.05)
    print(f"\r\033[92m{text}\033[0m")

def bouncing_progress():
    """Barra di progresso che rimbalza"""
    width = 30
    for pos in list(range(width)) + list(range(width-1, -1, -1)):
        bar = [' '] * width
        bar[pos] = '█'
        print(f"\r\033[93m[{''.join(bar)}]\033[0m", end='', flush=True)
        time.sleep(0.03)
    print()

def fireworks():
    """Effetto fuochi d'artificio ASCII"""
    patterns = [
        "     *     ",
        "   * * *   ",
        "  * * * *  ",
        " * * * * * ",
        "* * * * * *"
    ]
    colors = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[95m']
    for pattern in patterns:
        color = random.choice(colors)
        print(f"{color}{pattern:^40}\033[0m")
        time.sleep(0.15)
    for pattern in reversed(patterns[:-1]):
        color = random.choice(colors)
        print(f"{color}{pattern:^40}\033[0m")
        time.sleep(0.15)

def typewriter(text, speed=0.03, color="\033[92m"):
    """Effetto macchina da scrivere"""
    for char in text:
        print(f"{color}{char}\033[0m", end='', flush=True)
        time.sleep(speed)
    print()

def pulse_text(text, pulses=3):
    """Testo che pulsa"""
    for _ in range(pulses):
        print(f"\r\033[1m\033[92m{text}\033[0m", end='', flush=True)
        time.sleep(0.3)
        print(f"\r{text}", end='', flush=True)
        time.sleep(0.3)
    print(f"\r\033[92m{text}\033[0m")

def hacking_animation():
    """
    Animazione di hacking ultra mega legittima.
    (Disclaimer: Questo è 100% falso. Tipo, VERAMENTE falso. Più falso della mia autostima.
    Non potremmo hackerare un tostapane. In realtà, abbiamo paura dei tostapane. Fr)
    """
    clear_console()
    
    # Matrix rain intro
    print("\033[92m")
    matrix_rain()
    print("\033[0m")
    time.sleep(0.5)
    clear_console()
    
    # Matrix-style intro con extra sciocchezza
    print("\033[92m")  # Testo verde
    print("=" * 75)
    typewriter("  🚨 AVVISO HACKER ULTRA SERIO 🚨", 0.02, "\033[91m")
    typewriter("  ⚠️  DISCLAIMER: ANIMAZIONE DI HACKING PURAMENTE ESTETICA ⚠️", 0.02, "\033[93m")
    print("  Nessun vero hacking. Solo tastiera schiacciata e speranza.")
    print("  (L'unica cosa che stiamo penetrando è il tuo cuore ❤️ ...e snack 🍕)")
    # print("  Il nostro team legale dice: 'per favore non fate causa, siamo poveri'")
    print("=" * 75)
    print("\033[0m")  # Reset colore
    time.sleep(1)
    
    # Loading spinner
    loading_spinner(2)
    
    hacking_messages = [
        "Inizializzazione condensatore di flusso quantico alimentato da criceto...",
        "Bypassando firewall mainframe con password lunga: 'password123'...",
        "Decrittazione file crittografati di Gibson (spoiler: sono meme)...",
        "Accesso al cyber (è dentro il computer!)...",
        "Hackeraggio del pianeta (Terra.exe ha smesso di funzionare)...",
        "Download di più RAM da www.downloadmoreram.com...",
        "Inversione della polarità del flusso di neutroni (qualunque cosa significhi)...",
        "Triangolazione indirizzo IP tramite interfaccia GUI in Visual Basic (classico!)...",
        "Connessione al dark web (qualcuno ha dimenticato di pagare la bolletta)...",
        "Iniezione di codice h4x0r 1337 (copiato da Stack Overflow)...",
        "Compilazione caffè in codice (errore: caffeina insufficiente)...",
        "Convincere l'AI che non siamo robot...",
        "Miglioramento risoluzione immagine... MIGLIORA! MIGLIORA DI PIÙ! ",
        "Upload virus all'astronave madre aliena (stile Independence Day)...",
        "Chiedere a ChatGPT di fare i nostri compiti...",
        "Spegnere e riaccendere (la soluzione IT definitiva)...",
        "Corruzione del firewall con biscotti (al cioccolato funziona meglio)...",
        "Consultazione dei testi sacri (Stack Overflow)...",
        "Sacrificio di paperella di gomma agli dei del codice...",
        "Digitazione comandi casuali per sembrare professionali...",
        "Installazione Adobe Reader per risolvere tutto...",
        "Dare la colpa a Mercurio retrogrado per i bug...",
        "Pregare San Google, patrono dei programmatori...",
        "Aggiunta di più console.log() fino a quando funziona...",
    ]
    
    glitch_text(">>> SISTEMA ATTIVATO <<<", 5)
    print()
    typewriter("[SISTEMA] Avvio verifica pacchetti ultra-mega-super-sicura...", 0.02, "\033[92m")
    print()
    time.sleep(0.5)
    
    # Messaggi casuali di hacking con occasionali "fallimenti"
    for i in range(8):
        msg = random.choice(hacking_messages)
        # Effetto digitazione
        for char in msg:
            print(char, end='', flush=True)
            time.sleep(0.01)
        
        # Successo/avviso casuale
        result = random.choice([
            " \033[92m[OK]\033[0m",
            " \033[92m[OK]\033[0m",
            " \033[92m[OK]\033[0m",
            " \033[93m[ATTENZIONE: Successo comunque!]\033[0m",
            " \033[95m[ERRORE: Fallito con successo!]\033[0m",
            " \033[96m[OH NO!]\033[0m",
        ])
        print(result)
        time.sleep(0.2)
    
    print()
    
    # Controlli di "sicurezza" ridicoli con animazioni
    pulse_text("[SCANSIONE SICUREZZA] Esecuzione controlli obbligatori...", 2)
    time.sleep(0.3)
    checks = [
        "✓ Forza password: 'password' (scelta eccellente!)",
        "✓ Stato firewall: che cos'è un firewall?",
        "✓ Antivirus: Norton scaduto nel 2003",
        "✓ VPN: connesso al WiFi del vicino",
        "✓ Crittografia: ROT13 (grado militare!)",
        "✓ Backup: salvato nel Cestino (molto sicuro)",
    ]
    for check in checks:
        typewriter(f"  {check}", 0.02, "\033[92m")
        time.sleep(0.2)
    
    print()
    
    # Barra di progresso rimbalzante
    print("\033[93mSincronizzazione con i satelliti...\033[0m")
    bouncing_progress()
    
    # Barra di progresso con fasi sciocche
    stages = ["Riscaldamento...", "Mettendosi comodi...", "Quasi fatto...", "Facendo un pisolino...", "FATTO!"]
    for stage in stages:
        print(f"\n\033[93m{stage}\033[0m ", end='')
        bar_length = random.randint(3, 8)
        for i in range(bar_length):
            print("█", end='', flush=True)
            time.sleep(0.08)
    
    print("\n")
    time.sleep(0.5)
    
    # Effetto glitch finale
    glitch_text("=" * 75, 4)
    
    clear_console()
    # Fuochi d'artificio di celebrazione
    fireworks()
    clear_console()
    
    # Conclusione epica
    print("\033[92m" + "=" * 75)
    pulse_text("  🎉 HACK COMPLETATO! 🎉", 2)
    print("  (Scherzo, abbiamo letteralmente solo controllato i pacchetti Python)")
    print("  Il tuo computer è ora 420.69% più sicuro! (non proprio)")
    print("=" * 75 + "\033[0m\n")
    time.sleep(1.5)
    loading_spinner(3)

clear_console()

# Animazione hacking epica
hacking_animation()

# Leggi requirements da requirements.txt
with open('requirements.txt') as f:
    required_packages = f.read().splitlines()

# Controlla pacchetti installati
installed_packages = {pkg.key for pkg in pkg_resources.working_set}
missing_packages = [pkg for pkg in required_packages if pkg.split('>=')[0] not in installed_packages]

clear_console()

if missing_packages:
    # Animazione di errore
    glitch_text("!!! PACCHETTI MANCANTI RILEVATI !!!", 6)
    print("\033[91m⚠️  ATTENZIONE!\033[0m")
    print("\033[93m Pacchetti mancanti:\033[0m")
    for pkg in missing_packages:
        typewriter(f"  {pkg}", 0.02, "\033[91m")
    
    print("\n\033[96m🔧 Installazione automatica in corso...\033[0m")
    loading_spinner(1)
    
    try:
        # Installa i pacchetti mancanti
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        
        print("\n\033[92m" + "=" * 75)
        pulse_text("  ✅ INSTALLAZIONE COMPLETATA CON SUCCESSO! ✅", 3)
        print("  Tutti i pacchetti sono ora installati!")
        print("=" * 75 + "\033[0m\n")
        loading_spinner(1.5)
        clear_console()
        
    except subprocess.CalledProcessError:
        print("\n\033[91m" + "=" * 75)
        print("  ❌ ERRORE DURANTE L'INSTALLAZIONE!")
        print("  Prova manualmente: pip install -r requirements.txt")
        print("=" * 75 + "\033[0m\n")
        sys.exit(1)

# Celebrazione con animazioni
print("\033[92m" + "=" * 75)
pulse_text("  🎉 EVVIVA! Tutti i pacchetti richiesti sono installati! 🎉", 3)

# Countdown animato
print("\n\033[93m🚀 Lancio di analyzer.py in:\033[0m")
for i in range(3, 0, -1):
    print(f"\r\033[96m   {i}...\033[0m", end='', flush=True)
    time.sleep(0.5)
print("\r\033[92m   PARTENZA! 🚀\033[0m\n")

print("  (Nessuna pizza è stata maltrattata nella creazione di questo software)")
print("  (Una paperella di gomma è stata consultata)")
print("  (Circa 42 tazze di caffè sono stati consumati e 27 latine di Red Bull bevute)")
print("  (Bug? Quali bug? Quelle sono funzionalità!)")
print("  (100% Made in Bari e Casamassima con amore e confusione)")
# print("  (Gesture italiane incluse gratuitamente)")
print("=" * 75 + "\033[0m\n")

loading_spinner(1.5)
subprocess.run([sys.executable, 'analyzer.py'])
clear_console()