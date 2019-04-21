install wakeword detector from https://github.com/Picovoice/Porcupine.git  
in wakeword_detector.py modify following line:
    sys.path.append(os.path.join('/data/soft/Porcupine/binding/python/'))  
    to sys.path.append(os.path.join('/path/to/Porcupine/binding/python/'))

to add a wakeword:
- go to Porcupine root repository
- type
    tools/optimizer/linux/x86_64/pv_porcupine_optimizer -r resources/ -p linux -o . -w "<desired_keyword>"

