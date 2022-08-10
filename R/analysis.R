library(tidyverse)
library(forcats)

df <- read_csv('auto_data_cleaned.csv')

df %>% 
  mutate(body_type = factor(body_type)) %>%
  group_by(description, body_type) %>%
  ggplot(aes(x = fct_infreq(body_type))) + geom_histogram(stat="count") +
  scale_x_discrete(guide = guide_axis(angle=45))
  theme(axis.text.x = element_text(angle = 45, vjust=0.5))
  
df %>% 
    group_by(description, brand) %>%
    ggplot(aes(x = fct_infreq(brand))) + geom_histogram(stat="count") +
    scale_x_discrete(guide = guide_axis(angle=45))

df %>% 
  filter(brand %in% c('BMW','Mercedes-Benz')) %>% 
  group_by(brand, year_min) %>% 
  summarize(total = n()) %>%
  ggplot(aes(x = year_min, y = total)) + geom_col() + facet_wrap(brand~.)

mb <- df %>% 
  filter(brand == 'Mercedes-Benz') %>% 
  arrange(desc(year_min))
  
bmw <- df %>% 
  filter(brand == 'BMW') %>% 
  arrange(desc(year_min))


# Engine aspiration
df %>% 
  select(engine_aspiration, engine_model_code) %>% 
  unique() %>%
  ggplot(aes(x = fct_infreq(engine_aspiration))) + 
  geom_histogram(stat="count") +
  scale_x_discrete(guide = guide_axis(angle=45))

df %>% 
  select(year_min, engine_model_code, engine_aspiration) %>% 
  unique() %>% 
  filter(year_min > 1960) %>%
  group_by(year_min, engine_aspiration) %>% 
  summarize(total = n_distinct(engine_model_code)) %>%
  ggplot(aes(x = year_min, y = total, col=engine_aspiration)) + 
  geom_line() +
  scale_y_continuous(limits = c(0,200))

df %>% 
  select(year_min, engine_model_code, engine_aspiration) %>% 
  unique() %>% 
  filter(year_min > 1960) %>%
  mutate(engine_aspiration = case_when(str_detect(engine_aspiration, regex('turbo', ignore_case=T)) ~ 'Turbo',
                                        str_detect(engine_aspiration, regex('supercharger', ignore_case=T)) ~ 'Supercharger',
                                      is.na(engine_aspiration) ~ as.character('Naturally Aspirated')
                                      )) %>% 
  group_by(year_min, engine_aspiration) %>% 
  summarize(total = n()) %>%
  ggplot(aes(x = year_min, y = total, col=engine_aspiration)) + 
  geom_line() +
  scale_y_continuous(limits = c(0,300))


df %>% 
  filter(year_min > 2000) %>%
  group_by(year_min, powertrain_architecture) %>% 
  summarize(total = n()) %>%
  ggplot(aes(x = year_min, y = total, col=powertrain_architecture)) + 
  geom_line()

df %>% 
  filter(year_min > 2000) %>%
  mutate(fuel_type = case_when(str_detect(fuel_type, regex('/ electricity', ignore_case=T)) ~ 'Hybrid',
                               TRUE ~ fuel_type)) %>% 
  group_by(year_min, fuel_type) %>% 
  summarize(total=n()) %>% 
  ggplot(aes(x = year_min, y = total, col=fuel_type)) + 
  geom_line() +
  scale_y_continuous(limits=c(0,1100))

df %>% 
  select(year_min, engine_model_code, engine_aspiration) %>% 
  unique() %>% 
  filter(year_min > 1960) %>%
  mutate(engine_aspiration = case_when(str_detect(engine_aspiration, regex('turbo', ignore_case=T)) ~ 'Turbo',
                                       str_detect(engine_aspiration, regex('supercharger', ignore_case=T)) ~ 'Supercharger',
                                       (engine_aspiration=='Naturally aspirated engine' | is.na(engine_aspiration)) ~ as.character('Naturally Aspirated')
  )) %>% 
  group_by(year_min, engine_aspiration) %>% 
  summarize(total = n()) %>%
  ggplot(aes(x = year_min, y = total, fill=engine_aspiration)) + 
  # geom_bar(position="stack", stat="identity")
  geom_bar(position="fill", stat="identity")
  scale_y_continuous(limits = c(0,700))

  # Brands available in US
  us_brands <- df %>% 
    filter(!brand %in% c('Daihatsu', 'Citroen', 'Seat', 'Cupra', 'DS', 'Great Wall', 'Lada', 'MG',
                         'Renault', 'Skoda', 'Dacia', 'Haval', 'Vauxhall', 'Lancia', 'Peugeot')) %>%
    select(brand) %>% 
    unique()
  
  
  df %>% 
    select(year_min, fuel_econ_urban_mpg) %>%
    # group_by(year_min) %>%
    ggplot(aes(x = year_min, y = fuel_econ_urban_mpg, group=year_min)) +
    geom_boxplot()

  
  df %>% 
    ggplot(aes(x = engine_deplacement_cm3, y = power_hp, col = factor(number_of_cylinders))) + 
    geom_point()
  
  
  