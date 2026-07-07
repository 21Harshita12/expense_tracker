function question2_fractal_tree()
    %% QUESTION 2: Draw a Basic Recursive Fractal Tree
    % 1. Implements a recursive function that draws a line segment, then 
    %    two child branches rotated by +/-theta and scaled by factor s.
    % 2. Stops recursion when depth reaches maxDepth or branch length < minLength.
    % 3. Plots the tree with axis equal and no axes.

    clear;
    close all;
    clc;
    
    % Configuration parameters
    theta = pi/6;        % rotation angle (30 degrees in radians)
    s = 0.75;            % scaling factor (length scale)
    maxDepth = 10;       % maximum recursion depth
    minLength = 0.02;    % minimum branch length to draw
    
    % Initial trunk configuration
    x0 = 0; y0 = 0;      % start at root (bottom center)
    len = 1.0;           % length of initial trunk
    angle = pi/2;        % grow vertically upwards
    
    % Set up figure with custom aesthetics
    figure('Color', [0.95, 0.95, 0.95]);
    hold on;
    
    % Call the recursive function
    draw_branch(x0, y0, len, angle, 1, maxDepth, minLength, theta, s);
    
    % Apply plot settings
    axis equal;
    axis off;
    title('Recursive Fractal Tree (\theta = 30^\circ, s = 0.75)', 'FontSize', 14, 'FontWeight', 'bold');
    
    % Save high-resolution figure
    print(gcf, '-dpng', '-r300', 'question2_fractal_tree_octave.png');
    fprintf('Fractal tree plotted and saved successfully.\n');
end

function draw_branch(x0, y0, len, angle, depth, maxDepth, minLength, theta, s)
    % Termination criteria
    if depth > maxDepth || len < minLength
        return;
    end
    
    % Calculate end coordinates of the current branch segment
    x1 = x0 + len * cos(angle);
    y1 = y0 + len * sin(angle);
    
    % Make branches thinner and greener/lighter as depth increases
    % Base trunk is thick brown, outer branches are thin green
    trunk_color = [0.4, 0.25, 0.15]; % brown
    leaf_color = [0.1, 0.6, 0.2];    % green
    t = (depth - 1) / (maxDepth - 1); % interpolate color based on depth
    color = (1-t)*trunk_color + t*leaf_color;
    
    linewidth = max(0.5, 4.5 * (0.75^(depth-1)));
    
    % Plot current segment
    plot([x0, x1], [y0, y1], 'Color', color, 'LineWidth', linewidth);
    
    % Recurse left (+theta) and right (-theta) with scaled length and increased depth
    draw_branch(x1, y1, len * s, angle + theta, depth + 1, maxDepth, minLength, theta, s);
    draw_branch(x1, y1, len * s, angle - theta, depth + 1, maxDepth, minLength, theta, s);
end
