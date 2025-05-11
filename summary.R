# First, read the CSV file
file <- read.csv("user_candidate_support_detailed.csv")

library(dplyr)

file$support <- ifelse(file$support == "" | is.na(file$support), "Undecided", file$support)

summary <- file |>
  group_by(support) |>
  summarise(count = n())

print(summary)
write.csv(summary, "C:/Users/Admin/Desktop/xscrapsummary.csv", row.names = FALSE)