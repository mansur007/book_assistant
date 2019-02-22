# Audio Book Assistant - talk to your book

## What is it supposed to do?
- Listen to the user, wait for a command
    - wait for a keyword (Key Word Spotting, or KWS): *wait*, *hey*, *stop*, *pause*, etc.
    - wait for a button press
- Understand user's questions/commands related to the book. Sample Questions/Commands:
    - What is ***hegemony***?
    - Define ***social democracy***.
    - Translate ***unscrupulous***.
    - Translate last sentence.
    - Paraphrase last sentence.
    - What is synonym of ***rival***?  
    
    ! Note that user does NOT have to pronounce phrases/words perfectly. He/She might even be unaware of the spellings.  
    ! App will need to identify the command, its optional arguments, and the word/phrase/sentence to operate on
    
- Respond to commands/questions

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
    
    B) Speech -> [ASR] -> whole command as a sequence of phonemes and spaces(with timing)->  
    -> [parserB] -> (operand as a snippet from context, function, options).  
    parserB is similar to parserA, except that words are made of phonemes.  
    **Not started**.  
    
    C) Speech -> some features(e.g. spectrogram) with timing ->  
    -> [parserC] -> (operand as a snippet from context, function, options).  
    
    parserC takes each word's features as input and tries to see whether it matches a command, option,  
    or a snippet from the context.
    **Not started.**
    
