function question4_vectorized()
    %% QUESTION 4: Vectorized Mandelbrot Set & Interactive Sliders
    % 1. Vectorizes the Mandelbrot code to eliminate pixel loops.
    % 2. Saves high-resolution figures using print(gcf, '-dpng', '-r300', 'mandelbrot_vectorized.png').
    % 3. Uses a perceptually uniform colormap (parula).
    % 4. Creates interactive sliders using uicontrol for real-time parameter tuning.

    clear;
    close all;
    clc;

    % Initial default parameters
    global x_center y_center zoom_val max_iter fig ax_plot;
    x_center = -0.7;
    y_center = 0.0;
    zoom_val = 1.0;
    max_iter = 100;
    
    % Create UI Figure
    fig = figure('Name', 'Interactive Vectorized Mandelbrot', ...
                 'Position', [100, 100, 1000, 700], ...
                 'Color', [0.95, 0.95, 0.95]);
             
    % Setup plot axes
    ax_plot = axes('Parent', fig, 'Units', 'pixels', 'Position', [50, 120, 600, 520]);
    
    % Perform initial render
    update_plot();
    
    % Save initial high-resolution figure (as requested)
    print(fig, '-dpng', '-r300', 'mandelbrot_vectorized.png');
    fprintf('Initial vectorized high-resolution figure saved as mandelbrot_vectorized.png.\n');

    % Define UI controls panel
    uicontrol('Style', 'text', 'Position', [700, 600, 250, 30], ...
              'String', 'Mandelbrot Controls', 'FontSize', 12, 'FontWeight', 'bold', ...
              'BackgroundColor', [0.95, 0.95, 0.95], 'HorizontalAlignment', 'center');

    % Slider 1: X Center
    uicontrol('Style', 'text', 'Position', [700, 530, 250, 20], ...
              'String', 'Real Center (Re)', 'BackgroundColor', [0.95, 0.95, 0.95]);
    h_x = uicontrol('Style', 'slider', 'Min', -2.0, 'Max', 0.5, 'Value', x_center, ...
                    'Position', [700, 500, 250, 25], ...
                    'Callback', @(src, event) slider_callback(src, 'x'));

    % Slider 2: Y Center
    uicontrol('Style', 'text', 'Position', [700, 430, 250, 20], ...
              'String', 'Imag Center (Im)', 'BackgroundColor', [0.95, 0.95, 0.95]);
    h_y = uicontrol('Style', 'slider', 'Min', -1.25, 'Max', 1.25, 'Value', y_center, ...
                    'Position', [700, 400, 250, 25], ...
                    'Callback', @(src, event) slider_callback(src, 'y'));

    % Slider 3: Zoom
    uicontrol('Style', 'text', 'Position', [700, 330, 250, 20], ...
              'String', 'Zoom Factor', 'BackgroundColor', [0.95, 0.95, 0.95]);
    h_zoom = uicontrol('Style', 'slider', 'Min', 0.5, 'Max', 20.0, 'Value', zoom_val, ...
                       'Position', [700, 300, 250, 25], ...
                       'Callback', @(src, event) slider_callback(src, 'zoom'));

    % Slider 4: Max Iterations
    uicontrol('Style', 'text', 'Position', [700, 230, 250, 20], ...
              'String', 'Max Iterations', 'BackgroundColor', [0.95, 0.95, 0.95]);
    h_iter = uicontrol('Style', 'slider', 'Min', 10, 'Max', 300, 'Value', max_iter, ...
                       'Position', [700, 200, 250, 25], ...
                       'Callback', @(src, event) slider_callback(src, 'iter'));
end

% Callback function for interactive sliders
function slider_callback(src, param_type)
    global x_center y_center zoom_val max_iter;
    
    val = get(src, 'Value');
    switch param_type
        case 'x'
            x_center = val;
        case 'y'
            y_center = val;
        case 'zoom'
            zoom_val = val;
        case 'iter'
            max_iter = round(val);
    end
    
    % Re-render plot
    update_plot();
end

% Vectorized Mandelbrot Calculation and Plotting
function update_plot()
    global x_center y_center zoom_val max_iter ax_plot;
    
    % Resolution
    N = 400;
    
    % Calculate coordinates based on center and zoom
    width = 3.0 / zoom_val;
    height = 2.5 / zoom_val;
    
    x = linspace(x_center - width/2, x_center + width/2, N);
    y = linspace(y_center - height/2, y_center + height/2, N);
    [X, Y] = meshgrid(x, y);
    
    C = X + 1i*Y;
    Z = zeros(size(C));
    M = zeros(size(C));
    
    % Vectorized Loop: Computes all complex plane coordinates in parallel
    for iter = 1:max_iter
        % Find points that have not escaped yet (magnitude <= 2)
        mask = (Z .* conj(Z)) <= 4;
        
        % Update only active points in parallel
        Z(mask) = Z(mask).^2 + C(mask);
        M(mask) = iter;
    end
    
    % Render the vectorized matrix
    axes(ax_plot);
    imagesc(x, y, M);
    colormap(parula); % perceptually uniform colormap
    colorbar;
    axis image;
    xlabel('Re(c)');
    ylabel('Im(c)');
    title(sprintf('Vectorized Mandelbrot\nCenter: (%.2f, %.2f), Zoom: %.1fx, Iter: %d', ...
                  x_center, y_center, zoom_val, max_iter));
end
