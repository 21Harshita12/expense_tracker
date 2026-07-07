%% QUESTION 1: Mandelbrot Set Resolution Comparison
% Generates the Mandelbrot set at 400x400, 800x800, and 1600x1600.
% Measures rendering time and compares visual detail.

clear;
clc;
close all;

% Set up parameters
max_iter = 100;
xlim = [-2.0, 0.5];
ylim = [-1.25, 1.25];
resolutions = [400, 800, 1600];
times = zeros(length(resolutions), 1);

fprintf('=== MANDELBROT RESOLUTION COMPARISON ===\n');

figure('Name', 'Mandelbrot Resolution Comparison', 'Position', [100, 100, 1500, 500]);

for r = 1:length(resolutions)
    N = resolutions(r);
    fprintf('Rendering resolution %d x %d... ', N, N);
    
    % Initialize grid
    x = linspace(xlim(1), xlim(2), N);
    y = linspace(ylim(1), ylim(2), N);
    [X, Y] = meshgrid(x, y);
    C = X + 1i*Y;
    M = zeros(N, N);
    
    % Start timer
    tic;
    
    % Standard nested-loop Mandelbrot calculation
    for col = 1:N
        for row = 1:N
            c = C(row, col);
            z = 0;
            iter = 0;
            while abs(z) <= 2 && iter < max_iter
                z = z^2 + c;
                iter = iter + 1;
            end
            M(row, col) = iter;
        end
    end
    
    % Stop timer
    times(r) = toc;
    fprintf('Completed in %.4f seconds.\n', times(r));
    
    % Plot
    subplot(1, 3, r);
    imagesc(x, y, M);
    colormap(parula);
    colorbar;
    axis image;
    title(sprintf('Resolution: %d x %d\nTime: %.4f s', N, N, times(r)));
    xlabel('Re(c)');
    ylabel('Im(c)');
end

% Save the comparison figure as high resolution
print(gcf, '-dpng', '-r300', 'question1_mandelbrot_comparison_octave.png');
fprintf('\nTiming summary:\n');
for r = 1:length(resolutions)
    fprintf('Resolution %d x %d: %.4f seconds\n', resolutions(r), resolutions(r), times(r));
end
