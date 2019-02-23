# Audio Book Assistant - talk to your book

## What does it do?
- Play audio books
- Wait for a command of the user
    - voice: wait for a keyword (Key Word Spotting, or KWS): *wait*, *hey*, *stop*, *pause*, etc.
        - speaker recognition - react to the user's voice only
    - GUI: wait for a button press
- Understand user's questions/commands related to the book. Sample Questions/Commands:
    - What is ***hegemony***?
    - Define ***social democracy***.
    - Translate ***unscrupulous***.
    - Translate last sentence.
    - Paraphrase last sentence.
    - What is synonym of ***rival***?  
    
    ! Note that user does NOT have to pronounce phrases/words perfectly. He/She might be unaware of the correct spellings.  
    ! App will need to identify the command, its optional arguments, and the word/phrase/sentence to operate on
    
- Respond to commands/questions
    - Text on screen
    - Text2speech

- Provide basic functions of a good audio book app
    - player
    - playlist
    - variety of books
    - synchronous script
    
- Other very useful functions:
    - translator
    - dictionary
    - thesaurus
    - etc.  
    
    ! These functions should be accessible by both user's voice and device GUI.  
    ! These functions should utilize context to give the most relevant results.  



## Progress

- Spotting a command
    - button press, - Done
    - KWS, - Not started

- Understanding user's questions/commands  
    There are several ways:  
    A) Speech -> [ASR] -> whole command as a sequence of letters and spaces(with timing) ->  
    -> [parserA] -> (operand as a snippet from context, function, options).  
    
    parserA is a complex text processor which will compare words in the sequence to the function names and option names.  
    After finding the letters for a function and options - infer the operand phrase.
    **Done, but can be improved**
    
    B) Speech -> [ASR] -> whole command as a sequence of phonemes and spaces(with timing)->  
    -> [parserB] -> (operand as a snippet from context, function, options).  
    
    parserB is similar to parserA, except that words are made of phonemes.  
    **Not started**.  
    
    C) Speech -> some features(e.g. spectrogram) with timing ->  
    -> [parserC] -> (operand as a snippet from context, function, options).  
    
    parserC takes each word's features as input and tries to see whether it matches a command, option,  
    or a snippet from the context.
    **Not started.**  
    
- Respond to commands/questions
    - Text on screen. **Easily done for each new function**
    - Text2speech.  **Not Started**
    
- Provide basic functions of a good audio book app
    - player
        - key buttons: Play, Pause, Stop, Next, Previous, etc. Done, but still needs improvement - has some bugs and not convenient
            - After pressing *Next* or *Prev*, another track is selected but it can only be played after pressing *Stop* and then *Play*  
            It would be better if next or previous track starts playing immediately after pressing a corresponding button, provided that current track is playing.  
        - *go to* button is not working properly
            - *Play*, *go to 30* - stops, and when *Play* is pressed again - starts from beginning
            - *Play*, *pause*, *go to 30*, *play* - starts playing from beginning
            
    - playlist. **Done, but can be improved**
        - when user is asked for a directory with audio books - audio books themselves are not shown in the pop up window,
        only the directories that contain them are visible.
    - variety of books. **Not started**
    - synchronous script. **Done, although has some bugs**
        - text does NOT have a 100% match with the audio:
            - some utterances from audio are not present in text. Rare  

- Other very useful functions:
    - translator  
        google.api_core.exceptions.Forbidden: 403 POST https://translation.googleapis.com/language/translate/v2: Daily Limit Exceeded  
        
    - dictionary
    
        'define' and 'find' will be used for search in dictionary  
        
        user(U): *define invitation*  
        app(A): *definition of invitation: {'Noun': ['a request (spoken or written', 'a tempting allurement']}*  
            the returned output should be processed:  
                - get relevant part of speech  
                - get most relevant meaning  
        
        U: *define Netherfield*  
        A: *None*  
        U: *find tiresome*  
        A: *definition of tiresome!: None.* - The '!' must be removed before searching in dictionary  
    
    - thesaurus, etc., - to be added

