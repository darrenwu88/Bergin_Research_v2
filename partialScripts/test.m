

%5 7 9 10 12 14 16 17 19
pitch = 10000;

frqmod = [0.25 pi 1];


n_duration = [19 20 19 20 19 20 17 19 17 19 17 19 15 17 15 17 15 17 14 12 11; 
              0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.25 0.25 0.5];

n2_duration = [15 17 15 17 15 17 14 15 14 15 14 15 12 14 12 14 12 14 11 8 7; 
               0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.25 0.25 0.5];         

NOTE(pitch, n_duration, n2_duration);


function NOTE(pitch, n_duration, n2_duration)
    
    fs = pitch;
    for i = 1:length(n_duration)
        
        d = n_duration(2, i);
        d2 = n2_duration(2, i);
        
        A = 1;
        
        t = [0 : 1/fs : (d - (1/fs))];
        t2 = [0 : 1/fs : (d2 - (1/fs))];
        
        
        y = A * cos((2) * (pi) * ((220 * 2^(n_duration(1, i)/12 )) .* t));
        
        y2 = A * cos((2) * (pi) * ((220 * 2^(n2_duration(1, i)/12 )) .* t2));
        
        soundsc(y, fs);
        soundsc(y2, fs);
        
        pause(0.5);
    end
  %+ exp(t.^2 * pi/2)
end