#coding=utf-8
#qpy:kivy


import kivy
import cv2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.camera import Camera
from kivy.graphics.texture import Texture


cv2.setUseOptimized(True)


class CV2mera(Camera):
    firstFrame=None
    def _camera_loaded(self, *largs):
        if kivy.platform=='android':
            self.texture = Texture.create(size=self.resolution,colorfmt='rgb')
            self.texture_size = list(self.texture.size)
        else:
            super(CV2mera, self)._camera_loaded()

    def on_tex(self, *l):
        
        if kivy.platform=='android':
            buf = self._camera.grab_frame()
            if not buf:
                return
            frame = self._camera.decode_frame(buf)
            frame = self.process_frame(frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            if self.firstFrame is None:
                self.firstFrame = gray
            frameDelta = cv2.absdiff(self.firstFrame, gray)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
 
            # 扩展阀值图像填充孔洞，然后找到阀值图像上的轮廓
            thresh = cv2.dilate(thresh, None, iterations=2)
            (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
 
            # 遍历轮廓
            for c in cnts:
                # if the contour is too small, ignore it
                #if cv2.contourArea(c) < args["min_area"]:
                #    continue
 
                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                # 计算轮廓的边界框，在当前帧中画出该框
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
            buf = frame.tostring()
            self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        super(CV2mera, self).on_tex(*l)

    def process_frame(self,frame):
        r,g,b=cv2.split(frame)
        frame=cv2.merge((b,g,r))        
        rows,cols,channel=frame.shape
        M=cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
        dst=cv2.warpAffine(frame,M,(cols,rows))
        frame=cv2.flip(dst,1)
        if self.index==1:
            frame=cv2.flip(dst,-1)
        return frame

class MyLayout(BoxLayout):
    pass
class MainApp(App):
    def build(self):
        return MyLayout()
MainApp().run()