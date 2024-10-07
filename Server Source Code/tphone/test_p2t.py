from pix2text import Pix2Text,merge_line_texts
import argparse
import threading
import queue
import warnings
import onnxruntime

warnings.filterwarnings("ignore")

def image_reco(img_fp, img_quality, result_queue):
    p2t = Pix2Text(
        formula_config = dict(
        model_name='mfr', 
        model_backend='onnx',
        model_dir='path',  # Attention! Change to the path where the model file is stored!
        )
    )
    outs = p2t.recognize(img_fp, return_text=True)  # # can also use `p2t.recognize(img_fp)`
    result_queue.put(outs)

if __name__ == "__main__":
    print("Recoginzation activate")
    result_queue=queue.Queue()

    parser=argparse.ArgumentParser(description='Image to text')
    parser.add_argument('--image_path',type=str,help='Path to the image file')
    parser.add_argument('--image_quality', type=int,help='Image compression quality')
    args=parser.parse_args()

    warnings.filterwarnings("ignore")

    reco_handle=threading.Thread(target=image_reco,args=(args.image_path, args.image_quality, result_queue))
    reco_handle.start()
    
    reco_handle.join()

    result=result_queue.get()
    print("Text recognition START")
    print(result)
    print("Text recognition END")