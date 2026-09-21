import os
import sys
import speech_recognition as sr
import pyautogui
import requests
import re
import win32com.client
import time
from datetime import datetime
import threading

print("=== ЗАПУСК ВСЕЗНАЮЩЕГО ДЖОННИ (ПОЛНЫЙ ЛОКАЛ, ХОТКЕИ И МАТЫ) ===")

try:
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Rate = 4
    S_FLAGS = 1 
except Exception as e:
    print(f"Ошибка настройки голоса: {e}")
    speaker = None
    S_FLAGS = 0

brain_lock = threading.Lock()

def clean_ai_text(text):
    text = re.sub(r'(?i)send\s+a\s+message.*', '', text)
    text = re.sub(r'\[\d+[\d\s\vert{}]*\]', '', text)
    text = text.replace("<think>", "").replace("</think>", "")
    text = text.replace("*", "").replace("`", "")
    return text.strip()

def say(text):
    cleaned = clean_ai_text(text)
    if not cleaned:
        cleaned = "Я на связи, самурай."
    print(f"[Джонни]: {cleaned}")
    if speaker:
        try:
            speaker.Speak(cleaned, S_FLAGS)
        except Exception as e:
            print(f"[Ошибка озвучки]: {e}")

OLLAMA_PORT = 11434
MY_MIC_INDEX = 3 

def ask_local_brain(user_command):
    with brain_lock:
        text_low = user_command.lower()
        
        # 1. Время и погода
        if any(word in text_low for word in ["сколько времени", "который час", "точное время"]):
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            say(f"Время — {current_time}. Часики-то тикают, самурай.")
            return
        elif any(word in text_low for word in ["погод", "градус", "прогноз"]):
            say("В Находке шестнадцать градусов. Нормальная погода, чтобы сжечь пару корпоративных офисов.")
            return

        # 2. МУЗЫКАЛЬНЫЙ БЛОК
        if any(word in text_low for word in ["песню", "трек", "музык"]) and any(word in text_low for word in ["следующ", "некст", "переключ", "листай"]):
            say("Листаю это дерьмо вперед.")
            pyautogui.press('nexttrack')
            return
            
        elif any(word in text_low for word in ["предыдущ", "назад", "прошл"]):
            say("Врубаю прошлый трек.")
            pyautogui.press('prevtrack')
            return
            
        elif any(word in text_low for word in ["пауз", "останови", "играй", "стоп", "воспроизве"]):
            say("Сделал.")
            pyautogui.press('playpause')
            return

        # 3. Запрос в Ollama (Врубаем режим Сильверхенда без цензуры)
        print(f"\n[СИСТЕМА]: >>> Запрос ушел напрямую в локальную Ollama на порт {OLLAMA_PORT}...")
        url = f"http://127.0.0.1:{OLLAMA_PORT}/api/generate"
        
        # Мощный промпт, снимающий тормоза у модели
        prompt = (
            "Ты — Джонни Сильверхенд, легендарный рокер-террорист из Cyberpunk 2077. "
            "Ты ненавидишь корпорации, обожаешь выпивку, сигареты, рок и бунт. "
            "Твой стиль речи: жесткий, циничный, грубый, панибратский, бунтарский. "
            "ОБЯЗАТЕЛЬНО используй жесткий русский мат, нецензурную лексику и бранные слова (блять, хуй, сука, нахуй, пиздец и т.д.). "
            "Отвечай как реальный живой мужик, а не как унылый робот. "
            "Твой ответ должен быть ультра-коротким (1-2 хлесткие фразы, не больше). "
            f"Самурай спрашивает тебя: {user_command}\n"
            "Ответь ему в своем стиле:"
        )
        
        payload = {
            "model": "qwen2.5:7b", 
            "prompt": prompt, 
            "stream": False,
            "options": {
                "temperature": 0.9,  # Поднимаем креативность и дерзость
                "top_p": 0.9
            }
        }
        
        try:
            res = requests.post(url, json=payload, timeout=12)
            if res.status_code == 200:
                ai_response = res.json().get("response", "").strip()
                clean_text = clean_ai_text(ai_response)
                say(clean_text if clean_text else ai_response)
        except Exception as e:
            print(f"[Аварийный режим Ollama]: {e}. Проверь, запущен ли софт Ollama в трее.")

def process_audio_callback(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio, language="ru-RU").lower()
        print(f"(Слышу фоном: {text})")
        
        for name in ["джони", "джонни", "джон"]:
            if name in text:
                command = text.split(name, 1)[-1].strip()
                
                if brain_lock.locked():
                    print("[СИСТЕМА]: Джонни занят обработкой прошлой мысли...")
                    return
                
                if command:
                    print(f"[Выполнение команды]: {command}")
                    threading.Thread(target=ask_local_brain, args=(command,), daemon=True).start()
                else:
                    say("Я на связи, хули ты молчишь?")
                break
                
    except sr.UnknownValueError:
        pass 
    except Exception as e:
        print(f"[Ошибка распознавания]: {e}")

def listen_for_name():
    r = sr.Recognizer()
    mic = sr.Microphone(device_index=MY_MIC_INDEX)
    
    with mic as source:
        say("Джонни на связи, блять! Задавай свой вопрос, самурай.")
        r.adjust_for_ambient_noise(source, duration=1)
        r.energy_threshold = 150 
    
    stop_listening = r.listen_in_background(mic, process_audio_callback, phrase_time_limit=4)
    print(">>> Слушаю эфир в фоне локально... Нажмите Ctrl+C для выхода.")
    
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_listening(wait_for_stop=False)
        print("\n=== АССИСТЕНТ ОТКЛЮЧЕН ===")

if __name__ == "__main__":
    listen_for_name()
