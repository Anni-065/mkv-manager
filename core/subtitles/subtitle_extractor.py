import os

from core.analysis.track_analyzer import is_forced_subtitle_by_name
from core.subtitles.subtitle_converter import convert_subtitle_to_srt, is_srt_format
from core.utils.subprocess_utils import run_hidden

try:
    from ..config.config import MKVMERGE_PATH
except ImportError:
    from ..config.config_example import MKVMERGE_PATH


def extract_and_convert_subtitles(file_path, output_folder, subtitle_tracks):
    """Extract subtitles from MKV and convert non-SRT formats to SRT"""
    mkvextract_path = MKVMERGE_PATH.replace("mkvmerge", "mkvextract")

    if not os.path.exists(mkvextract_path):
        print(f"⚠️ mkvextract not found at {mkvextract_path}")
        return []

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    converted_subtitles = []

    for track in subtitle_tracks:
        track_id = track["id"]
        lang = track["lang"]
        forced = track.get("forced", False)
        hearing_impaired = track.get("hearing_impaired", False)
        track_name = track.get("track_name", "")

        name_based_forced = is_forced_subtitle_by_name(track_name)
        actual_forced = forced or name_based_forced

        suffix = ""
        if actual_forced:
            suffix += ".forced"
        if hearing_impaired:
            suffix += ".sdh"

        temp_subtitle_file = os.path.join(
            output_folder, f"{base_name}.{lang}{suffix}.temp")
        final_srt_file = os.path.join(
            output_folder, f"{base_name}.{lang}{suffix}.srt")

        try:
            cmd = [mkvextract_path, "tracks", file_path,
                   f"{track_id}:{temp_subtitle_file}"]

            result = run_hidden(cmd, capture_output=True, text=True)

            if result.returncode == 0 and os.path.exists(temp_subtitle_file):
                if temp_subtitle_file.endswith('.srt') or is_srt_format(temp_subtitle_file):
                    os.rename(temp_subtitle_file, final_srt_file)
                    converted_subtitles.append(final_srt_file)

                    print(f"✅ Extracted SRT subtitle: {final_srt_file}")
                else:
                    success, message = convert_subtitle_to_srt(
                        temp_subtitle_file, final_srt_file)

                    if success:
                        converted_subtitles.append(final_srt_file)
                        print(
                            f"✅ Converted subtitle to SRT: {final_srt_file} ({message})")
                    else:
                        print(
                            f"⚠️ Could not convert subtitle {temp_subtitle_file} to SRT: {message}")

                    try:
                        os.remove(temp_subtitle_file)
                    except OSError:
                        pass
            else:
                print(
                    f"⚠️ Failed to extract subtitle track {track_id}: {result.stderr}")

        except Exception as e:
            print(f"⚠️ Error processing subtitle track {track_id}: {str(e)}")

            for temp_file in [temp_subtitle_file, final_srt_file]:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except OSError:
                    pass

    return converted_subtitles
