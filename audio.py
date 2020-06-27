import discord
from pydub import AudioSegment
import asyncio
import logging
import discord.opus as opus
import pydub

OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

class SineAudio(discord.AudioSource):

    def __init__(self):
        self.theta = 0
        self.phi = 0

    def read(self):
        bit_rate = 48000
        bit_depth = 16
        duration = 20e-3
        gain = int(20000/3)
        freq1 = 554.365261954
        freq2 = 830.60939516
        freq3 = 698.456462866
        frame_rate = int(3840/2/2)
        data = []
        sample_rate = 48000
        # for theta in np.linspace(self.phi, self.phi + duration, frame_rate):
        for i in range(self.phi, self.phi + frame_rate):
            d = 0
            d += int(math.sin(i/(sample_rate) * freq1 * 2 * math.pi) * gain)
            d += int(math.sin(i/(sample_rate) * freq2 * 2 * math.pi) * gain)
            d += int(math.sin(i/(sample_rate) * freq3 * 2 * math.pi) * gain)
            #d2 = int(math.sin(theta * 880 * 2 * math.pi) * gain)
            data.extend(d.to_bytes(2, byteorder='little', signed=True))
            data.extend([0, 0])
        self.phi += frame_rate
            
        '''
        for i in range(self.phi, self.phi + int(sample_rate * duration)):
            d = int(math.sin(self.theta)* gain)
            self.theta = i / (bit_rate * bit_depth * duration) * 2 * math.pi * freq
            data.extend(d.to_bytes(2, byteorder='little', signed=True))
        self.phi += int(sample_rate * duration)
        '''

        return bytes(data)

    def is_opus(self):
        return False

    def cleanup(self):
        print("Cleaning up", flush = True)

frame_size = 3840


class YTAudio(discord.AudioSource):
    
    def __init__(self, url, channel):
        print("here", flush = True)
        self.theta = 0
        self.phi = 0
        self.url = url
        self.data_iter = None
        self.data = bytearray([])
        self.message = None
        self.done = False
        self.channel = channel

        try:
            video = pafy.new(url)
            self.video = video
            self.time = 0
            hash_object = hashlib.md5(url.encode())
            best_url = video.getbestaudio().url
            url_hash = hash_object.hexdigest()

            print(best_url, flush = True)
            curl_proc = Popen(['curl', '-L', '-s', best_url], stdout=PIPE)
            # print(curl_proc.stderr, flush = True)
            
            ffmpeg_proc = Popen(['./audio/ffmpeg.exe', '-i', 'pipe:0', '-f', 's16le', '-acodec', 'pcm_s16le', '-'], stdin=curl_proc.stdout, stdout=PIPE)
            curl_proc.stdout.close() 
            # out, err = ffmpeg_proc.communicate()
            self.data_iter = iter(lambda: ffmpeg_proc.stdout.read(1024), '')

            self.buffer = []

            #time.sleep(10)
        except Exception as e:
            print(str(e), flush = True)

    async def update_msg(self):
        if self.done:
            return


        msg = f"{self.video.title} \n Time: {str(datetime.timedelta(seconds=round(self.time)))} \n Buffer Len: {round(len(self.data) / (frame_size / 20e-3), 2)}s  [{len(self.data)} bytes]"
        if not self.done and self.message == None:
            self.message = await self.channel.send(msg)
        else:
            await self.message.edit(content = msg)


    def read(self):
        data = []
        self.time += 20e-3
        if self.data_iter == None:
            return bytes([])

        try:
            while True: #len(self.data) < frame_size:
                n = next(self.data_iter)
                if not n:
                    break
                self.data.extend(n)
        except StopIteration:
            print("DONE", flush = True)
            self.data_iter = None
            return bytes(data)
        except Exception as e:
            print(str(e), flush = True)

        if self.data:
            data = self.data[:frame_size]
            del self.data[:frame_size]
        return bytes(data)



    def is_opus(self):
        return False

    def cleanup(self):
        print("Cleaning up", flush = True)
        self.done = True

def create_YTAudio(url, channel):
    return YTAudio(url, channel)
    # asyncio.get_event_loop().run_until_complete(yt.init_(url, channel))

async def load_opus_lib(opus_libs=OPUS_LIBS):
    try:
        if opus.is_loaded():

            return True

        for opus_lib in opus_libs:
            try:
                opus.load_opus(opus_lib)
                return
            except OSError:
                pass

        raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))
    except Exception as e:
        print(str(e), flush = True)
