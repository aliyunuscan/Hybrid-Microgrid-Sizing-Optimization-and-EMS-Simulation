% =========================================================================
% MICROGRID SYSTEM ANALYSIS & FINANCIAL EVALUATION (GNU OCTAVE)
% =========================================================================
clear all; close all; clc;

disp('Starting Microgrid Engineering Analysis...');

% 1. DATA IMPORT (Read the results from Python Simulation)
% We skip the first row (header) and first column (Datetime strings)
file_path = '/home/ayunusc/Desktop/Microgrid_Project/analysis/simulation_results.csv';
data = csvread(file_path, 1, 1);

% Extract Columns based on Python output structure
P_load     = data(:, 3);
Total_Gen  = data(:, 5);
P_unmet    = data(:, 8);
P_dumped   = data(:, 9);

% =========================================================================
% 2. RELIABILITY ANALYSIS (LPSP)
% =========================================================================
Total_Annual_Load = sum(P_load);
Total_Unmet_Load  = sum(P_unmet);

if Total_Annual_Load > 0
    LPSP = (Total_Unmet_Load / Total_Annual_Load) * 100;
else
    LPSP = 0;
end

if LPSP < 2.0
    status_rel = 'EXCELLENT (Highly Reliable System)';
elseif LPSP < 5.0
    status_rel = 'ACCEPTABLE (Standard Reliability)';
else
    status_rel = 'POOR (System sizing is too small!)';
end

% =========================================================================
% 3. FINANCIAL ANALYSIS (LCOE - Levelized Cost of Energy)
% =========================================================================
Project_Lifetime = 20;       
Discount_Rate    = 0.08;     
Inverter_Life    = 10;       
Battery_Life     = 7;        

Cost_PV      = 50 * 150;     
Cost_Wind    = 5000;         
Cost_Battery = 20 * 300;     
Cost_Inv     = 2000;         
Total_CAPEX  = Cost_PV + Cost_Wind + Cost_Battery + Cost_Inv;

Annual_OPEX = Total_CAPEX * 0.02; 

Rep_Inv  = Cost_Inv / ((1 + Discount_Rate)^Inverter_Life);
Rep_Bat1 = Cost_Battery / ((1 + Discount_Rate)^Battery_Life);
Rep_Bat2 = Cost_Battery / ((1 + Discount_Rate)^(Battery_Life*2));
Total_Replacement = Rep_Inv + Rep_Bat1 + Rep_Bat2;

Total_Cost_NPV = Total_CAPEX + Total_Replacement;
Total_Energy_NPV = 0;

for year = 1:Project_Lifetime
    Total_Cost_NPV = Total_Cost_NPV + (Annual_OPEX / ((1 + Discount_Rate)^year));
    Degraded_Energy = sum(Total_Gen) * ((1 - 0.005)^year);
    Total_Energy_NPV = Total_Energy_NPV + (Degraded_Energy / ((1 + Discount_Rate)^year));
end

LCOE = Total_Cost_NPV / Total_Energy_NPV;

Grid_Price = 0.10; 
if LCOE < Grid_Price
    status_fin = 'HIGHLY PROFITABLE (Cheaper than grid!)';
else
    status_fin = 'EXPENSIVE (Needs optimization or grants)';
end

% =========================================================================
% 4. EFFICIENCY METRICS (Energy Wasted)
% =========================================================================
Total_Dumped = sum(P_dumped);
Dump_Ratio = (Total_Dumped / sum(Total_Gen)) * 100;

% =========================================================================
% 5. REPORT GENERATION (Save to TXT and Print to Console)
% =========================================================================

output_dir = '/home/ayunusc/Desktop/Microgrid_Project/analysis';
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

report_path = fullfile(output_dir, 'engineering_report.txt');
fid = fopen(report_path, 'w');


if fid == -1
    error('CRITICAL ERROR: Octave dosyayı oluşturamadı. Lütfen yetkileri kontrol edin.');
end

print_both = @(fmt, varargin) ...
    arrayfun(@(x) fprintf(x, fmt, varargin{:}), [1, fid]);

print_both('\n==================================================\n');
print_both(' MICROGRID ENGINEERING & FINANCIAL REPORT\n');
print_both('==================================================\n\n');

print_both('--------------------------------------------------\n');
print_both(' 1. TECHNICAL RELIABILITY (LPSP)\n');
print_both('--------------------------------------------------\n');
print_both('Total Annual Load Demand : %.2f kWh/year\n', Total_Annual_Load);
print_both('Total Unmet Load (Outage): %.2f kWh/year\n', Total_Unmet_Load);
print_both('LPSP (Outage Probability): %.4f %%\n', LPSP);
print_both('Status                   : %s\n\n', status_rel);

print_both('--------------------------------------------------\n');
print_both(' 2. FINANCIAL FEASIBILITY (LCOE)\n');
print_both('--------------------------------------------------\n');
print_both('Initial Investment (CAPEX) : $ %.2f\n', Total_CAPEX);
print_both('Total Lifecycle Cost (NPV) : $ %.2f\n', Total_Cost_NPV);
print_both('LCOE (Cost per kWh)        : $ %.4f / kWh\n', LCOE);
print_both('Investment Verdict         : %s\n\n', status_fin);

print_both('--------------------------------------------------\n');
print_both(' 3. SYSTEM EFFICIENCY\n');
print_both('--------------------------------------------------\n');
print_both('Total Wasted Energy (Dump) : %.2f kWh/year\n', Total_Dumped);
print_both('Wasted Energy Ratio        : %.2f %%\n', Dump_Ratio);
print_both('--------------------------------------------------\n');

fclose(fid);
disp(['SUCCESS: Report successfully saved to -> ', report_path]);