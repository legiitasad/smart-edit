import os
import subprocess
import shutil


#   MEDIA TOOL v2.1 - Video Cut + Image Insert
#   Banaya gaya: Tumhare liye bhai


def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] ffmpeg installed nahi hai!")
        print("[TIP] Yahan se install karo: https://ffmpeg.org/download.html")
        return False

def get_media_duration(media_path):
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', media_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return None

def cut_media(input_path, output_path, start_time, duration):
    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-ss', str(start_time),
        '-t', str(duration),
        '-c', 'copy',
        '-avoid_negative_ts', 'make_zero',
        output_path
    ]
    try:
        subprocess.run(cmd, check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] Cut karne mein problem aayi!")
        return False

def remove_segment(input_path, output_path, start_time, duration, file_ext):
    end_time = start_time + duration

    first_part  = f"temp_first{file_ext}"
    second_part = f"temp_second{file_ext}"

    cmd1 = ['ffmpeg', '-y', '-i', input_path, '-t', str(start_time), '-c', 'copy', first_part]
    cmd2 = ['ffmpeg', '-y', '-i', input_path, '-ss', str(end_time),  '-c', 'copy', second_part]
    cmd3 = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'concat_list.txt', '-c', 'copy', output_path]

    try:
        subprocess.run(cmd1, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        with open("concat_list.txt", "w") as f:
            f.write(f"file '{first_part}'\n")
            f.write(f"file '{second_part}'\n")

        subprocess.run(cmd3, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for f in [first_part, second_part, "concat_list.txt"]:
            if os.path.exists(f):
                os.remove(f)
        return True

    except subprocess.CalledProcessError:
        print("[ERROR] Remove karne mein problem aayi!")
        for f in [first_part, second_part, "concat_list.txt"]:
            if os.path.exists(f):
                os.remove(f)
        return False


#   IMAGE INSERT FEATURE


def get_video_resolution(video_path):
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=p=0',
        video_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        parts = result.stdout.strip().split(',')
        return int(parts[0]), int(parts[1])
    except:
        return None, None

def insert_image_in_video(video_path, image_path, output_path, start_time, duration,
                           position, opacity, scale_percent):
    vid_w, vid_h = get_video_resolution(video_path)
    if vid_w is None:
        print("[ERROR] Video resolution nahi nikal paaya!")
        return False

    scale_w = int(vid_w * scale_percent / 100)
    padding = 20
    pos_map = {
        'topleft':     f"{padding}:{padding}",
        'topright':    f"W-w-{padding}:{padding}",
        'bottomleft':  f"{padding}:H-h-{padding}",
        'bottomright': f"W-w-{padding}:H-h-{padding}",
        'center':      f"(W-w)/2:(H-h)/2",
    }
    overlay_pos = pos_map.get(position, pos_map['bottomright'])
    end_time = start_time + duration

    filter_complex = (
        f"[1:v]scale={scale_w}:-1,"
        f"format=rgba,"
        f"colorchannelmixer=aa={opacity}[img];"
        f"[0:v][img]overlay={overlay_pos}:enable='between(t,{start_time},{end_time})'[out]"
    )

    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', image_path,
        '-filter_complex', filter_complex,
        '-map', '[out]',
        '-map', '0:a?',
        '-c:v', 'libx264',
        '-c:a', 'copy',
        '-preset', 'fast',
        '-crf', '18',
        output_path
    ]

    try:
        subprocess.run(cmd, check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] Image insert karne mein problem aayi!")
        return False


def image_insert_menu(current_folder):
    print("\n" + "="*50)
    print("  IMAGE INSERT MODE")
    print("="*50)

    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    video_files = [f for f in os.listdir(current_folder)
                   if any(f.lower().endswith(ext) for ext in video_extensions)]

    if not video_files:
        print("[ERROR] Is folder mein koi video file nahi mili!")
        return

    print("\n[AVAILABLE] Video files:")
    for v in video_files:
        size = os.path.getsize(os.path.join(current_folder, v)) / (1024 * 1024)
        print(f"  - {v} ({size:.1f} MB)")

    while True:
        selected_video = input("\n[INPUT] Konsi VIDEO file mein image daalni hai? ").strip()
        video_path = os.path.join(current_folder, selected_video)
        if os.path.exists(video_path) and any(selected_video.lower().endswith(e) for e in video_extensions):
            break
        print(f"[ERROR] '{selected_video}' nahi mili! Dobara try karo.")

    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']
    image_files = [f for f in os.listdir(current_folder)
                   if any(f.lower().endswith(ext) for ext in image_extensions)]

    if not image_files:
        print("[ERROR] Is folder mein koi image file nahi mili!")
        print("[TIP] PNG, JPG, JPEG, BMP, GIF, WEBP supported hain.")
        return

    print("\n[AVAILABLE] Image files:")
    for img in image_files:
        size = os.path.getsize(os.path.join(current_folder, img)) / (1024 * 1024)
        print(f"  - {img} ({size:.2f} MB)")

    while True:
        selected_image = input("\n[INPUT] Konsi IMAGE insert karni hai? ").strip()
        image_path = os.path.join(current_folder, selected_image)
        if os.path.exists(image_path) and any(selected_image.lower().endswith(e) for e in image_extensions):
            break
        print(f"[ERROR] '{selected_image}' nahi mili! Dobara try karo.")

    vid_duration = get_media_duration(video_path)
    if vid_duration is None:
        print("[ERROR] Video ki duration nahi nikal paaya!")
        return

    minutes = int(vid_duration // 60)
    seconds = vid_duration % 60
    print(f"\n[TIME] Video duration: {vid_duration:.2f}s ({minutes}m {seconds:.1f}s)")

    try:
        print("\n" + "-"*50)
        start_time = float(input(f"[INPUT] Image kab se dikhni chahiye? (seconds, 0 to {vid_duration:.1f}): "))
        if not (0 <= start_time < vid_duration):
            print("[ERROR] Start time range se bahar hai!")
            return

        max_dur = vid_duration - start_time
        img_duration = float(input(f"[INPUT] Kitni der tak dikhni chahiye? (seconds, max {max_dur:.1f}): "))
        if img_duration <= 0 or start_time + img_duration > vid_duration:
            print("[ERROR] Duration galat hai!")
            return
    except ValueError:
        print("[ERROR] Number dalo bhai!")
        return

    print("\n[INPUT] Image kahan rakhni hai?")
    positions = {'1': 'topleft', '2': 'topright', '3': 'bottomleft', '4': 'bottomright', '5': 'center'}
    for k, v in positions.items():
        print(f"  {k}. {v}")
    pos_choice = input("Position choose karo (1-5, default 4): ").strip()
    position = positions.get(pos_choice, 'bottomright')

    try:
        opacity_input = input("[INPUT] Opacity (0.1 to 1.0, default 1.0): ").strip()
        opacity = float(opacity_input) if opacity_input else 1.0
        opacity = max(0.1, min(1.0, opacity))
    except ValueError:
        opacity = 1.0

    try:
        scale_input = input("[INPUT] Size - video width ka % (5-80, default 20): ").strip()
        scale_percent = float(scale_input) if scale_input else 20.0
        scale_percent = max(5.0, min(80.0, scale_percent))
    except ValueError:
        scale_percent = 20.0

    name_without_ext, ext = os.path.splitext(selected_video)
    img_name_clean = os.path.splitext(selected_image)[0]
    output_name = f"{name_without_ext}_with_{img_name_clean}{ext}"
    output_path = os.path.join(current_folder, output_name)

    print("\n" + "="*50)
    print("[SUMMARY]")
    print(f"  Video    : {selected_video}")
    print(f"  Image    : {selected_image}")
    print(f"  Show at  : {start_time:.1f}s to {start_time + img_duration:.1f}s")
    print(f"  Position : {position}")
    print(f"  Opacity  : {opacity}")
    print(f"  Size     : {scale_percent:.0f}% of video width")
    print(f"  Output   : {output_name}")
    print("="*50)

    confirm = input("\n[CONFIRM] Theek hai? (y/n): ").strip().lower()
    if confirm != 'y':
        print("[CANCELLED] Cancel ho gaya!")
        return

    print("\n[PROGRESS] Image insert ho rahi hai, zara ruko...")
    if insert_image_in_video(video_path, image_path, output_path,
                              start_time, img_duration, position, opacity, scale_percent):
        out_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n[OK] Output file bana di: {output_name} ({out_size:.2f} MB)")
        print("[DONE] Kaam ho gaya bhai!")
    else:
        print("[ERROR] Kuch gadbad ho gayi image insert mein!")



#   VIDEO / AUDIO CUT FEATURE


def video_cut_menu(current_folder):
    print("\n" + "="*50)
    print("  VIDEO / AUDIO CUT MODE")
    print("="*50)

    media_extensions = ['.mp3', '.m4a', '.wav', '.flac', '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    media_files = []

    for file in os.listdir(current_folder):
        if any(file.lower().endswith(ext) for ext in media_extensions):
            media_files.append(file)

    if not media_files:
        print("[ERROR] Is folder mein koi media file nahi mili!")
        print("[TIP] Supported: MP3, MP4, AVI, MOV, MKV, WAV, FLAC, etc.")
        return

    print("[AVAILABLE] Media files:")
    for media in media_files:
        try:
            size = os.path.getsize(os.path.join(current_folder, media)) / (1024 * 1024)
            ext = os.path.splitext(media)[1].lower()
            file_type = "AUDIO" if ext in ['.mp3', '.m4a', '.wav', '.flac'] else "VIDEO"
            print(f"  - {media} ({file_type}, {size:.1f} MB)")
        except:
            print(f"  - {media}")

    print("\n" + "="*50)
    while True:
        selected_file = input("[INPUT] Konsi file cut karni hai? (ex: song.mp3 or video.mp4): ").strip()

        if not selected_file:
            print("[ERROR] Kuch to likho bhai!")
            continue

        file_path = os.path.join(current_folder, selected_file)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            if any(selected_file.lower().endswith(ext) for ext in media_extensions):
                break
            else:
                print(f"[ERROR] '{selected_file}' supported file nahi hai!")
                print("[TIP] Supported: .mp3, .mp4, .avi, .mov, .mkv, .wav, etc.")
        else:
            print(f"[ERROR] '{selected_file}' ye file is folder mein nahi mili!")
            print("[TIP] Available files hain:")
            for media in media_files:
                print(f"  - {media}")

    file_ext = os.path.splitext(selected_file)[1].lower()
    is_video = file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']

    print(f"\n[INFO] Processing '{selected_file}'...")
    duration = get_media_duration(file_path)
    if duration is None:
        print("[ERROR] File ki duration nahi nikal paaye!")
        return

    minutes = int(duration // 60)
    seconds = duration % 60
    media_type = "VIDEO" if is_video else "AUDIO"
    print(f"\n[TIME] {media_type} duration: {duration:.2f} seconds")
    if minutes > 0:
        print(f"       ({minutes} minute {seconds:.2f} seconds)")
    else:
        print(f"       ({seconds:.2f} seconds)")

    try:
        print("\n" + "-"*50)
        start_time = float(input("[INPUT] Kahan se cut karna hai? (seconds): "))

        if start_time < 0 or start_time > duration:
            print(f"[ERROR] Start time 0 se {duration:.2f} ke beech mein hona chahiye!")
            return

        max_cut = duration - start_time
        cut_duration = float(input(f"[INPUT] Kitna cut karna hai? (seconds, max {max_cut:.2f}): "))

        if cut_duration <= 0 or start_time + cut_duration > duration:
            print("[ERROR] Cut duration galat hai!")
            return

        end_time = start_time + cut_duration

        print("\n" + "="*50)
        print("[SUMMARY]")
        print(f"  File: {selected_file}")
        print(f"  Type: {media_type}")
        print(f"  Cut from: {start_time:.2f}s to {end_time:.2f}s")
        print(f"  Cut duration: {cut_duration:.2f} seconds")
        print("="*50)

        confirm = input("\n[CONFIRM] Kya aap confirm karte hain? (y/n): ").strip().lower()

        if confirm != 'y':
            print("[CANCELLED] Cancel ho gaya!")
            return

        name_without_ext, ext = os.path.splitext(selected_file)
        backup_name = f"backup_{selected_file}"
        backup_path = os.path.join(current_folder, backup_name)

        print(f"\n[PROGRESS] Backup bana raha hun...")
        shutil.copy2(file_path, backup_path)
        print(f"[OK] Backup saved: {backup_name}")

        cut_file_name = f"{name_without_ext}_cut_{start_time}to{end_time}{ext}"
        cut_file_path = os.path.join(current_folder, cut_file_name)

        print(f"\n[PROGRESS] Cutting segment...")
        if cut_media(file_path, cut_file_path, start_time, cut_duration):
            cut_size = os.path.getsize(cut_file_path) / (1024 * 1024)
            print(f"[OK] Cut segment saved: {cut_file_name} ({cut_size:.2f} MB)")

            remaining_file_name = f"{name_without_ext}_remaining{ext}"
            remaining_file_path = os.path.join(current_folder, remaining_file_name)

            print(f"\n[PROGRESS] Removing cut segment from original...")
            if remove_segment(file_path, remaining_file_path, start_time, cut_duration, ext):
                remaining_size = os.path.getsize(remaining_file_path) / (1024 * 1024)
                print(f"[OK] Remaining file saved: {remaining_file_name} ({remaining_size:.2f} MB)")

                print("\n" + "="*50)
                print("[FINAL SUMMARY]")
                print("="*50)
                print(f"1. [BACKUP]    {backup_name}")
                print(f"2. [CUT PART]  {cut_file_name} ({cut_size:.2f} MB)")
                print(f"3. [REMAINING] {remaining_file_name} ({remaining_size:.2f} MB)")
                print("="*50)
                print("\n[DONE] Kaam ho gaya bhai!")
            else:
                print("[ERROR] Remaining file banane mein error aaya!")
        else:
            print("[ERROR] Cut karne mein error aaya!")
            shutil.copy2(backup_path, file_path)
            print("[INFO] Original file restore kar di gayi!")

    except ValueError:
        print("[ERROR] Sahi time dalo bhai! (number dalo, jaise 15 ya 7.5)")
    except Exception as e:
        print(f"[ERROR] Kuch gadbad ho gayi: {e}")


# ============================================================
#   MAIN MENU
# ============================================================

def print_banner():
    print("\n" + "="*52)
    print("=                                                  =")
    print("=      MEDIA TOOL v2.1  -  Bhai ka tool           =")
    print("=   Video/Audio Cut  +  Image Insert              =")
    print("=                                                  =")
    print("="*52)

def main():
    if not check_ffmpeg():
        return

    current_folder = os.getcwd()
    print_banner()

    while True:
        print(f"\n[INFO] Current folder: {current_folder}")
        print("\n" + "="*52)
        print("  MAIN MENU - Kya karna hai bhai?")
        print("="*52)
        print("  1.  Video / Audio CUT karna hai")
        print("  2.  Video mein IMAGE insert karni hai")
        print("  3.  Exit (band karo program)")
        print("="*52)

        choice = input("\n[INPUT] Option choose karo (1 / 2 / 3): ").strip()

        if choice == '1':
            video_cut_menu(current_folder)
        elif choice == '2':
            image_insert_menu(current_folder)
        elif choice == '3':
            print("\n[BYE] Program band ho raha hai. Allah Hafiz!\n")
            break
        else:
            print("[ERROR] Bhai sirf 1, 2 ya 3 likho!")
            continue

        print("\n" + "-"*52)
        again = input("[INPUT] Wapas menu pe jaana hai? (y/n): ").strip().lower()
        if again != 'y':
            print("\n[BYE] Program band ho raha hai. Allah Hafiz!\n")
            break

if __name__ == "__main__":
    main()