data <- read.csv('~/Documents/Langs/Even/apply/corpora_by_speakers.csv', stringsAsFactors = T)
summary(data)
all.morphs <- unique(data$morpheme)
lms <- c()
aovs <- c()
morphs <- c()
for(mor in all.morphs[1:5]) {
  ds <- data[data$morpheme == mor, ];
  if(length(unique(ds$corpus))==2){
  lms <- c(lms, lm(ds$count~ds$corpus+ds$speaker));
  aovs <- c(aovs, aov(ds$count~ds$corpus))
  morphs <- c(morphs, mor)}
}

print(length(all.morphs))
print(length(morphs))

lms[1]
aovs[1]
aov(ds$count~ds$corpus)
