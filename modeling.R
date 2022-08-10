
df %>% 
  ggplot(aes(x = power_hp/curb_weight_lb, y = log(acceleration_0_62_mph), col = factor(number_of_cylinders))) + 
  geom_point() 
# + facet_grid(number_of_cylinders~.)

df_mod <- df %>% 
  mutate(engine_aspiration = case_when(str_detect(engine_aspiration, regex('turbo', ignore_case=T)) ~ 'Turbo',
                                       # str_detect(engine_aspiration, regex('supercharger', ignore_case=T)) ~ 'Supercharger',
                                       # (engine_aspiration=='Naturally aspirated engine') ~ as.character('Naturally Aspirated'))
                                       TRUE ~ 'Not Turbo')) %>%
  select(acceleration_0_62_mph, 
         power_hp, 
         curb_weight_lb, 
         number_of_cylinders,
         piston_stroke_mm,
         cyl_bore_mm,
         engine_aspiration) %>%
  distinct() %>% 
  na.omit()
                                       
model <- lm(log(acceleration_0_62_mph) ~ (power_hp/curb_weight_lb) + 
              number_of_cylinders +
              piston_stroke_mm +
              cyl_bore_mm + 
              factor(engine_aspiration),
            data = df_mod)
model
summary(model)


model <- lm(log(power_hp) ~ 
              factor(number_of_cylinders) +
              piston_stroke_mm +
              cyl_bore_mm +
              factor(engine_aspiration), data = df_mod)
summary(model)


df_mod %>% ggplot(aes(x = number_of_cylinders, y = log(power_hp))) + geom_point()

                  