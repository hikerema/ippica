import tkinter as tk
from tkinter import messagebox
import random
import pygame
from gtts import gTTS
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Inizializza pygame per gli effetti sonori
pygame.mixer.init()

# Carica gli effetti sonori
sound_start = pygame.mixer.Sound("audio/start_race.wav")
sound_end = pygame.mixer.Sound("audio/end_race.wav")
sound_win = pygame.mixer.Sound("audio/win.wav")
sound_lose = pygame.mixer.Sound("audio/lose.wav")

# Funzione per riprodurre un messaggio vocale
def play_voice_message(message):
    tts = gTTS(message, lang='it')
    tts.save("message.mp3")
    pygame.mixer.music.load("message.mp3")
    pygame.mixer.music.play()

class HorseRaceBettingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scommesse Corse dei Cavalli")
        self.geometry("800x600")

        # Inizializza variabili
        self.balance = 1000
        self.horses = ["Cavallo 1", "Cavallo 2", "Cavallo 3", "Cavallo 4", "Cavallo 5"]
        self.odds = [2.0, 3.0, 5.0, 4.0, 3.5]
        self.horse_colors = ["red", "blue", "green", "orange", "purple"]
        self.selected_horse = tk.StringVar(value=self.horses[0])
        self.bet_amount = tk.IntVar(value=100)
        self.progress = [0] * 5

        # Crea interfaccia grafica
        self.create_widgets()

        # Inizializza modello di machine learning
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.X = []
        self.y = []
        self.trained = False

        # Numero di corse giocate
        self.races_played = 0

    def create_widgets(self):
        # Etichetta del saldo
        self.balance_label = tk.Label(self, text=f"Saldo: {self.balance} monete", font=("Helvetica", 16))
        self.balance_label.pack(pady=10)

        # Etichetta del cavallo attualmente selezionato
        self.current_horse_label = tk.Label(self, text=f"Cavallo attualmente selezionato: {self.selected_horse.get()}", font=("Helvetica", 14))
        self.current_horse_label.pack(pady=10)

        # Canvas per visualizzare la corsa
        self.canvas = tk.Canvas(self, width=750, height=600, bg="white")
        self.canvas.pack(pady=20)

        # Rettangoli dei cavalli
        self.horse_rects = [
            self.canvas.create_rectangle(50, 100 + i*80, 110, 140 + i*80, fill=color) 
            for i, color in enumerate(self.horse_colors)
        ]

    def start_race(self):
        # Inizia la corsa
        sound_start.play()
        self.progress = [0] * 5 
        self.update_race()

    def update_race(self):
        # Aggiorna la posizione dei cavalli durante la corsa
        race_finished = False
        for i in range(5):
            self.progress[i] += random.randint(1, 5)
            if self.progress[i] >= 650:
                winner = i
                race_finished = True
                break

        # Pulisce il canvas e ridisegna i cavalli
        self.canvas.delete("all")
        self.horse_rects = [
            self.canvas.create_rectangle(50 + self.progress[i], 100 + i*80, 110 + self.progress[i], 140 + i*80, fill=color) 
            for i, color in enumerate(self.horse_colors)
        ]

        if race_finished:
            self.finish_race(winner)
        else:
            self.after(100, self.update_race)

    def finish_race(self, winner):
        # Gestisce la fine della corsa
        sound_end.play()
        if winner == self.selected_horse_index:
            winnings = self.bet_amount_value * self.odds[winner]
            self.balance += winnings
            sound_win.play()
            play_voice_message(f"Hai vinto! Guadagni {winnings} monete. Il tuo nuovo saldo è: {self.balance} monete")
        else:
            self.balance -= self.bet_amount_value
            sound_lose.play()
            play_voice_message(f"Hai perso. Il tuo nuovo saldo è: {self.balance} monete")
        
        self.balance_label.config(text=f"Saldo: {self.balance} monete")
        self.update_training_data(winner)
        self.reset_game()
        self.play_automatically()

    def update_training_data(self, winner):
        # Aggiorna i dati di addestramento
        self.X.append([self.selected_horse_index])
        self.y.append(winner == self.selected_horse_index)
        if len(self.X) > 10:  # Addestra il modello dopo 10 corse
            self.model.fit(self.X, self.y)
            self.trained = True

    def predict_best_horse(self):
        # Prevede il cavallo migliore da scommettere
        if self.trained:
            predictions = self.model.predict_proba([[i] for i in range(5)])
            predicted_horse = np.argmax([p[1] for p in predictions])
            return predicted_horse
        else:
            return random.randint(0, 4)

    def play_automatically(self):
        # Gioca automaticamente
        self.selected_horse_index = self.predict_best_horse()
        self.selected_horse.set(self.horses[self.selected_horse_index])
        self.current_horse_label.config(text=f"Cavallo attualmente selezionato: {self.selected_horse.get()}")
        self.bet_amount_value = 100  # Fissa la scommessa a 100 per semplicità
        self.start_race()

    def reset_game(self):
        # Reset del gioco
        self.progress = [0] * 5
        self.canvas.delete("all")
        self.horse_rects = [
            self.canvas.create_rectangle(50, 100 + I*80, 110, 140 + I*80, fill=color) 
            for I, color in enumerate(self.horse_colors)
        ]

if __name__ == "__main__":
    app = HorseRaceBettingApp()
    app.after(1000, app.play_automatically)  # Inizia a giocare automaticamente dopo 1 secondo
    app.mainloop()

    # Pulisce i file audio creati per la voce
    if os.path.exists("message.mp3"):
        os.remove("message.mp3")