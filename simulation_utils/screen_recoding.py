import os
import time
import shutil
import threading

class ScreenRecorder:
    def __init__(self, output_file, driver):
        self.driver = driver

        if not os.path.exists(os.path.sep.join(output_file.split(os.path.sep)[:-1])):
            raise ValueError("please create path")

        self.output_file = output_file
        self.exit = False
        self.final_lock = threading.Semaphore(0)
        self.fps = 25

    def _restart_folder(self,folder):
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.mkdir(folder)

    def record_screen_thread(self):
        self._restart_folder("temp")

        index = 0
        try:
            while not self.exit:
                frame_name = f"temp/tmp_{index}.png"
                self.driver.save_screenshot(frame_name)
                index+=1
                time.sleep(1/self.fps) 
        finally:        
            self.final_lock.release()
        

    def start_recording(self):
        recording_thread = threading.Thread(target=self.record_screen_thread)
        recording_thread.start()

    def stop_recording(self):
        self.exit = True
        self.final_lock.acquire()
        if os.path.exists("temp") and len(os.listdir("temp")) > 0:
            os.system(f"ffmpeg -r {self.fps} -i temp/tmp_%01d.png -vcodec mpeg4 -y {self.output_file}.mp4")
            shutil.rmtree("temp")
            return True
        else:
            return False
        
