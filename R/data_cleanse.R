library(tidyverse)
library(magrittr)

get_raw_data <- function(){
  setwd("../")
  df <- read_csv(paste0(getwd(), "/python/full_data_raw.csv"))
  setwd(paste0(getwd(), "/R"))
  return(df)
}

raw_data <- get_raw_data() %>%
  janitor::clean_names()

raw_data %>% select(-colnames(raw_data[colSums(is.na(raw_data))==nrow(raw_data)]))

remove_na_cols <- function(df){
  fully_na_cols <- colnames(raw_data[colSums(is.na(df))>=nrow(df)*0.9])
  df_out <- df %>% select(-fully_na_cols)
  print(paste0('Removed ', length(df_out), ' columns.'))
  return(df_out)
}

df_narm <- remove_na_cols(raw_data)

# Begin building new dataset 
df_clean <- df_narm %>% select(title, 
                          description, 
                          brand,
                          model,
                          generation,
                          modification_engine,
                          powertrain_architecture
                          )

# Add character columns that don't need cleaning as factors
temp <- df_narm %>%
  select(fuel_type,
         engine_location_25,
         engine_model_code,
         position_of_cylinders,
         engine_aspiration,
         front_suspension,
         rear_suspension,
         front_brakes,
         rear_brakes,
  ) %>% 
  mutate_all(factor)

df_clean <- cbind(df_clean, temp)

# Generation years
temp <- df_narm %>% 
  mutate(year_min = as.numeric(str_extract(start_of_production, '[0-9]*')), 
         year_max = as.numeric(str_extract(end_of_production, '[0-9]*'))
         ) %>% 
  select(year_min, year_max)

df_clean <- cbind(df_clean, temp)

# Body type
temp <- df_narm %>% 
  mutate(body_type = factor(str_split(body_type, ",", simplify=TRUE)[,1])) %>% 
  select(body_type)

df_clean <- cbind(df_clean, temp)

# Vehicles with ranges instead of a single number are only a small minority
# of the dataset. We will use the first number across the board.
temp <- df_narm %>% 
  mutate(seats = case_when(
    str_detect(seats, "-|/") ~ substr(seats, 1, 1),
    TRUE ~ seats),
    seats = as.numeric(seats)) %>%
  select(seats)

df_clean <- cbind(df_clean, temp)

# Same treatment for doors
temp <- df_narm %>%
  mutate(doors = case_when(
    str_detect(doors, "-|/") ~ substr(doors, 1, 1),
    TRUE ~ doors),
    doors = as.numeric(doors)) %>% 
  select(doors)

df_clean <- cbind(df_clean, temp)

# pulling the first part of the field and converting it for the mpg value
temp <- df_narm %>% mutate(# urban
              fuel_econ_urban_lp100km = as.numeric(str_split(fuel_consumption_economy_urban, 
                                                  " l/100 km\r\n\t\t\t\t\t\t\t", 
                                                  simplify = TRUE)[,1]),
              fuel_econ_urban_mpg = 235.215/fuel_econ_urban_lp100km*1.00,
              
              # extra urban
              fuel_econ_extra_urban_lp100km = as.numeric(str_split(fuel_consumption_economy_extra_urban, 
                                                             " l/100 km\r\n\t\t\t\t\t\t\t", 
                                                             simplify = TRUE)[,1]),
              fuel_econ_extra_urban_mpg = 235.215/fuel_econ_extra_urban_lp100km*1.00
              ) %>% 
  select(fuel_econ_urban_lp100km,
         fuel_econ_urban_mpg,
         fuel_econ_extra_urban_lp100km,
         fuel_econ_extra_urban_mpg)

df_clean <- cbind(df_clean, temp)


temp <- df_narm %>% 
  mutate(acceleration_0_100_km_h = str_replace(acceleration_0_100_km_h, " |<|>", ""),
         acceleration_0_100_km_h = str_replace(acceleration_0_100_km_h, "sec", ""),
         acceleration_0_100_km_h = str_split(acceleration_0_100_km_h,
                                             "-",
                                             simplify=TRUE)[,1],
         acceleration_0_100_km_h = as.numeric(acceleration_0_100_km_h)) %>% 
  mutate(acceleration_0_62_mph = acceleration_0_100_km_h) %>% 
  mutate(acceleration_0_60_mph_calculated_by_auto_data_net = str_replace(acceleration_0_60_mph_calculated_by_auto_data_net, " |<|>", ""),
         acceleration_0_60_mph_calculated_by_auto_data_net = str_replace(acceleration_0_60_mph_calculated_by_auto_data_net, "sec", ""),
         acceleration_0_60_mph_calculated_by_auto_data_net = str_split(acceleration_0_60_mph_calculated_by_auto_data_net,
                                             "-",
                                             simplify=TRUE)[,1],
         acceleration_0_60_mph_calculated = as.numeric(acceleration_0_60_mph_calculated_by_auto_data_net)) %>% 
  select(acceleration_0_100_km_h,
         acceleration_0_62_mph,
         acceleration_0_60_mph_calculated)

df_clean <- cbind(df_clean, temp)

# max speed
temp <- df_narm %>% 
  mutate(max_speed_kmh = as.numeric(str_split(df_narm$maximum_speed, " km/h", simplify=TRUE)[,1]),
         max_speed_mph = max_speed_kmh / 1.609) %>% 
  select(max_speed_kmh, max_speed_mph)

df_clean <- cbind(df_clean, temp)

# power
df_clean$power_hp <- str_split(df_narm$power, " Hp", simplify=TRUE)[,1] %>% as.numeric()

df_clean$power_hp_rpm <- str_split(
  str_split(df_narm$power, "@ ", simplify=TRUE)[,2], 
  " rpm", simplify=TRUE)[,1] %>% 
  as.numeric()

df_clean$torque_nm <- str_split(df_narm$torque, " Nm", simplify=TRUE)[,1] %>% 
  as.numeric()

df_clean$torque_nm_rpm <- str_split(
  str_split(df_narm$torque, "@ ", simplify=TRUE)[,2],
  " rpm", simplify=TRUE)[,1] %>% 
  as.numeric()

# engine measures
df_clean$engine_deplacement_cm3 <- str_split(df_narm$engine_displacement, 
                                       " cm3",
                                       simplify=TRUE)[,1] %>% as.numeric()

df_clean$cyl_bore_mm <- str_split(df_narm$cylinder_bore, 
                            " mm",
                            simplify=TRUE)[,1] %>% as.numeric()

df_clean$piston_stroke_mm <- str_split(df_narm$piston_stroke,
                                 " mm",
                                 simplify=TRUE)[,1] %>% as.numeric()

df_clean$curb_weight_kg <- str_split(df_narm$kerb_weight,
                               " kg",
                               simplify=TRUE)[,1] %>% as.numeric()

extract_mm <- function(x){
  x_out <- str_split(x, "/| mm|-", simplify=TRUE)[,1] %>%
    as.numeric()
  return(x_out)
}

df_clean$length_mm <- extract_mm(df_narm$length)
df_clean$width_mm <- extract_mm(df_narm$width)
df_clean$height_mm <- extract_mm(df_narm$height)
df_clean$wheelbase_mm <- extract_mm(df_narm$wheelbase)
df_clean$front_track_mm <- extract_mm(df_narm$front_track)
df_clean$rear_back_track_mm <- extract_mm(df_narm$rear_back_track)

# Number of gears
temp <- df_narm %>% 
  mutate(gears_automatic = as.numeric(str_extract(number_of_gears_automatic_transmission, "[0-9]*")),
         gears_manual = as.numeric(str_extract(number_of_gears_manual_transmission, "[0-9]*"))) %>% 
  select(gears_automatic, gears_manual)

df_clean <- cbind(df_clean, temp)

# Add numeric columns from original dataset that don't need transformation
temp <- df_narm %>% 
  keep(is.numeric)

df_clean <- cbind(df_clean, temp)

# Tires sizes
tire_code_pattern <- "[0-9]{3}/[0-9]{2} ([A-Z]{2}|[A-Z]{1})( |[0-9]*| [0-9]*)"

temp <- df_narm %>% 
  mutate(front_tires = case_when(
    str_detect(df_narm$tires_size, "Front") ~ str_extract(tires_size, tire_code_pattern)
    ),
    rear_tires = case_when(
      str_detect(df_narm$tires_size, "Rear") ~ str_split(tires_size, "Rear",simplify=TRUE)[,2]
    ),
    rear_tires = str_extract(rear_tires, tire_code_pattern),
    tires_size_all = case_when(is.na(front_tires) & is.na(rear_tires) ~ str_extract(tires_size, tire_code_pattern))
  ) %>% select(front_tires, rear_tires, tires_size_all)

tire_code_parse <- function(tire_str, comp){
  int_out <- if(comp == "width") {
    as.numeric(str_split(tire_str, "/", simplify=TRUE)[,1])
  } else if(comp == "ar"){
    as.numeric(str_split(str_split(tire_str, "/", simplify=TRUE)[,2],
      " ", simplify=TRUE)[,1])
  } else if(comp == "diam"){
    as.numeric(str_extract(str_split(tire_str, " ", simplify=TRUE)[,2], "[0-9].*"))
  } else if(comp == "cons"){
    str_extract(str_split(tire_str, " ", simplify=TRUE)[,2], "[A-Z]*")
  }
  return(int_out)
}

temp <- temp %>% 
mutate(front_tire_width = tire_code_parse(front_tires, "width"),
         front_tire_aspect_ratio = tire_code_parse(front_tires, "ar"),
         front_tire_construction = tire_code_parse(front_tires, "cons"),
         front_tire_diam = tire_code_parse(front_tires, "diam"),
       
         rear_tire_width = tire_code_parse(rear_tires, "width"),
         rear_tire_aspect_ratio = tire_code_parse(rear_tires, "ar"),
         rear_tire_construction = tire_code_parse(rear_tires, "cons"),
         rear_tire_diam = tire_code_parse(rear_tires, "diam"),
       
         all_tire_width = tire_code_parse(tires_size_all, "width"),
         all_tire_aspect_ratio = tire_code_parse(tires_size_all, "ar"),
         all_tire_construction = tire_code_parse(tires_size_all, "cons"),
         all_tire_diam = tire_code_parse(tires_size_all, "diam"))
  

df_clean <- cbind(df_clean, temp)

# Calculate metric to imperial etc.
df$curb_weight_lb <- round(df$curb_weight_kg * 2.20462, 1)

# TODO - valvetrain
# df_narm %>% mutate(valvetrain_new = case_when(str_detect(valvetrain, 'dohc|DOHC') ~ 'DOHC',
                                         # str_detect(valvetrain, 'SOHC|sohc') ~ 'SOHC',
                                         # str_detect(valvetrain, '')))


write_csv(df_clean, 'auto_data_cleaned.csv')
