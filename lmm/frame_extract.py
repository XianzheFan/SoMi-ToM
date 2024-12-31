import cv2
import os

def extract_frames(video_path, num_frames):
    video_capture = cv2.VideoCapture(video_path)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    
    frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
    os.makedirs('extracted_frames', exist_ok=True)
    
    for i, frame_index in enumerate(frame_indices):
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = video_capture.read()
        
        if ret:
            frame_filename = f'extracted_frames/frame_{i+1}.jpg'
            cv2.imwrite(frame_filename, frame)
            print(f"Save photo: {frame_filename}")

    video_capture.release()

video_path = 'videos\chest_random_2.mp4'
extract_frames(video_path, 5)
