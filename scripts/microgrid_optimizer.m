% =========================================================================
% MICROGRID SIZING OPTIMIZATION (REAL-WORLD CAPEX FOCUS)
% =========================================================================
clear all; close all; clc;

disp('==================================================');
disp(' STARTING MICROGRID CAPACITY OPTIMIZATION');
disp('==================================================');

% 1. BULLETPROOF DATA IMPORT
file_path = '/home/ayunusc/Desktop/Microgrid_Project/analysis/simulation_results.csv';
disp('Reading 1-year simulation data...');

dataMatrix = csvread(file_path, 1, 1);

P_load       = dataMatrix(:, 4);
P_solar_base = dataMatrix(:, 5); % Based on 50m2
P_wind       = dataMatrix(:, 6); % Remains constant (5kW turbine)

% 2. DEFINE SEARCH SPACE
Base_Area = 50.0; 
Area_Range = 50:25:250;  
Batt_Range = 20:20:200;  

% Matrices to store results for 3D Plotting
LPSP_Matrix = zeros(length(Batt_Range), length(Area_Range));
CAPEX_Matrix = zeros(length(Batt_Range), length(Area_Range)); % LCOE yerine CAPEX izliyoruz

% Tracking variables for the "Golden Ratio" (Minimum CAPEX focus)
Best_CAPEX = inf;
Best_Area = 0;
Best_Batt = 0;
Best_LPSP = 0;

Total_Combinations = length(Area_Range) * length(Batt_Range);
fprintf('Testing %d different hardware combinations. Please wait...\n', Total_Combinations);

% 3. START GRID SEARCH LOOP
for a = 1:length(Area_Range)
    current_area = Area_Range(a);
    P_solar_current = P_solar_base * (current_area / Base_Area);
    
    for b = 1:length(Batt_Range)
        current_batt = Batt_Range(b);
        
        % --- A. RUN 8760-HOUR BATTERY SIMULATION ---
        P_net = P_solar_current + P_wind - P_load;
        current_energy = current_batt; 
        min_energy = current_batt * 0.20; 
        max_energy = current_batt;
        
        unmet_total = 0;
        
        for i = 1:8760
            current_energy = current_energy + P_net(i);
            if current_energy > max_energy
                current_energy = max_energy;
            elseif current_energy < min_energy
                unmet_total = unmet_total + (min_energy - current_energy);
                current_energy = min_energy;
            end
        end
        
        % --- B. CALCULATE LPSP ---
        total_load = sum(P_load);
        if total_load > 0
            current_lpsp = (unmet_total / total_load) * 100;
        else
            current_lpsp = 0;
        end
        LPSP_Matrix(b, a) = current_lpsp;
        
        % --- C. CALCULATE CAPEX ---
        Cost_PV = current_area * 150;     
        Cost_Wind = 5000;                 
        Cost_Battery = current_batt * 300;
        Cost_Inv = 2000;
        Total_CAPEX = Cost_PV + Cost_Wind + Cost_Battery + Cost_Inv;
        
        CAPEX_Matrix(b, a) = Total_CAPEX;
        
        % --- D. FIND THE OPTIMUM (REAL-WORLD LOGIC) ---
        % Condition: LPSP < 2% AND Absolute Minimum Initial Investment
        if current_lpsp <= 2.0 && Total_CAPEX < Best_CAPEX
            Best_CAPEX = Total_CAPEX;
            Best_Area = current_area;
            Best_Batt = current_batt;
            Best_LPSP = current_lpsp;
        end
    end
end

% =========================================================================
% 4. PRINT AND SAVE OPTIMAL RESULTS
% =========================================================================
output_dir = '/home/ayunusc/Desktop/Microgrid_Project/analysis';
report_path = fullfile(output_dir, 'optimization_report.txt');
fid = fopen(report_path, 'w');

print_both = @(fmt, varargin) ...
    arrayfun(@(x) fprintf(x, fmt, varargin{:}), [1, fid]);

print_both('\n==================================================\n');
print_both(' OPTIMIZATION COMPLETE: REAL-WORLD GOLDEN RATIO\n');
print_both('==================================================\n\n');

if Best_Area == 0
    print_both('WARNING: No combination achieved LPSP < 2.0%%.\n');
    print_both('You need to increase the limits of Area_Range or Batt_Range.\n');
else
    print_both('Optimal Solar Panel Area       : %d m2\n', Best_Area);
    print_both('Optimal Battery Capacity       : %d kWh\n', Best_Batt);
    print_both('Resulting LPSP (Outage)        : %.2f %%\n', Best_LPSP);
    print_both('--------------------------------------------------\n');
    print_both('Minimum Initial Invest (CAPEX) : $ %d\n', Best_CAPEX);
end

fclose(fid);
disp(['SUCCESS: Text report saved to -> ', report_path]);

% =========================================================================
% 5. 3D VISUALIZATION AND SAVE TO IMAGE
% =========================================================================
[X, Y] = meshgrid(Area_Range, Batt_Range);
fig = figure('Name', 'Microgrid Sizing Optimization Surface', 'Position', [100, 100, 1200, 550]);

% Plot 1: CAPEX Surface
subplot(1, 2, 1);
surf(X, Y, CAPEX_Matrix);
title('Initial Investment / CAPEX ($)', 'FontSize', 12, 'FontWeight', 'bold');
xlabel({''; 'Solar Panel Area (m^2)'}, 'FontSize', 10);
ylabel({'Battery Capacity (kWh)'; ''}, 'FontSize', 10);
zlabel('CAPEX ($)', 'FontSize', 10);
colorbar;
shading interp;
view(-45, 35);

% Plot 2: LPSP Surface
subplot(1, 2, 2);
surf(X, Y, LPSP_Matrix);
title('LPSP (Reliability %)', 'FontSize', 12, 'FontWeight', 'bold');
xlabel({''; 'Solar Panel Area (m^2)'}, 'FontSize', 10);
ylabel({'Battery Capacity (kWh)'; ''}, 'FontSize', 10);
zlabel('LPSP (%)', 'FontSize', 10);
colorbar;
shading interp;
view(-45, 35);

disp('Displaying 3D Optimization Surfaces...');

set(fig, 'PaperUnits', 'inches');
set(fig, 'PaperPosition', [0 0 16 8]); 
set(fig, 'PaperSize', [16 8]);

img_path = fullfile(output_dir, 'optimization_surfaces.png');
print(fig, img_path, '-dpng', '-r300');
disp(['SUCCESS: 3D Graphics saved to -> ', img_path]);