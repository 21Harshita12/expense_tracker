%% QUESTION 3: Julia Set 5x5 Gallery
% Samples c from a 5x5 grid in the complex plane [real: -0.8 to 0.8, imag: -0.8 to 0.8].
% Generates Julia sets for each c and identifies connected vs. disconnected sets.

clear;
clc;
close all;

% Grid definitions for sampling c
re_c = linspace(-0.8, 0.8, 5);
im_c = linspace(-0.8, 0.8, 5);

% Resolution for each individual Julia set plot
N = 200;
max_iter = 100;
z_lim = 1.5;

% Set up coordinates for Julia set calculation
x = linspace(-z_lim, z_lim, N);
y = linspace(-z_lim, z_lim, N);
[X, Y] = meshgrid(x, y);

figure('Name', 'Julia Set 5x5 Gallery', 'Position', [100, 100, 1200, 1200], 'Color', [0.95, 0.95, 0.95]);

fprintf('=== JULIA SET GALLERY ANALYSIS ===\n');
fprintf('%-5s | %-16s | %-12s | %s\n', 'Plot', 'c value', 'Mandelbrot?', 'Connectivity');
fprintf('-------------------------------------------------------------\n');

plot_idx = 1;
for r = 1:5
    for col = 1:5
        % Note: row r corresponds to imaginary part (from top to bottom, 0.8 to -0.8)
        % column col corresponds to real part (from left to right, -0.8 to 0.8)
        c = re_c(col) + 1i * im_c(6-r);
        
        % Calculate Julia set for this c
        Z = X + 1i*Y;
        M = zeros(N, N);
        for iter = 1:max_iter
            mask = abs(Z) <= 2;
            Z(mask) = Z(mask).^2 + c;
            M(mask) = iter;
        end
        
        % Connectivity test: Julia set is connected iff the orbit of z=0 is bounded
        % (i.e. if c is inside the Mandelbrot set). We check the orbit of 0.
        z_orbit = 0;
        is_bounded = true;
        for iter = 1:200
            z_orbit = z_orbit^2 + c;
            if abs(z_orbit) > 2
                is_bounded = false;
                break;
            end
        end
        
        % Determine label
        if is_bounded
            connectivity_str = 'Connected';
            mandelbrot_str = 'Inside';
        else
            connectivity_str = 'Disconnected';
            mandelbrot_str = 'Outside';
        end
        
        fprintf('%-5d | %6.2f + %5.2fi | %-12s | %s\n', ...
            plot_idx, real(c), imag(c), mandelbrot_str, connectivity_str);
        
        % Plot the Julia set
        subplot(5, 5, plot_idx);
        imagesc(x, y, M);
        colormap(parula); % using parula style
        axis off;
        axis image;
        
        % Annotate with the c value and connectivity type
        title(sprintf('c = %.2f+%.2fi\n%s', real(c), imag(c), connectivity_str), 'FontSize', 8);
        
        plot_idx = plot_idx + 1;
    end
end

% Save the gallery figure
print(gcf, '-dpng', '-r300', 'question3_julia_gallery_octave.png');
fprintf('\n5x5 Julia gallery saved successfully as question3_julia_gallery_octave.png.\n');
