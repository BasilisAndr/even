data <- read.csv('~/Documents/Langs/Even/apply/corpora_by_speakers.csv', stringsAsFactors = T)
summary(data)
all.morphs <- unique(data$morpheme)
lms <- c()
morphs <- c()
for(mor in all.morphs) {
  ds <- data[data$morpheme == mor, ];
  if(length(unique(ds$corpus))==2){
  lms <- c(lms, lm(ds$count~ds$corpus+ds$speaker));
  morphs <- c(morphs, mor)}
}

print(length(all.morphs))
print(length(morphs))

lms[1]
