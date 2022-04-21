means <- read.csv(file= '/nas/longleaf/home/jyhh/AllMeans_MASK_NO_WEIGHT_WM_Seg_mean.csv')
numPairs <-(ncol(means)-2)/2
numSamples <- nrow(means)
rightSide <- means[3:13]
leftSide <- means[14:ncol(means)]
list <- list()
for (i in 1:numSamples){
  vector <- vector()
  
  for (j in 1:numPairs){
    numerator <- leftSide[i,j] -rightSide[i,j]
    denominator <- leftSide[i,j] + rightSide[i,j]
    value <- numerator/denominator
    vector <- append(vector, value)
  }
  vsum <- vector()
  vsum <-append(vsum, sub(".*sepLabel_", "", means[i,1]))
  vsum <-append(vsum, sum(vector[2:numPairs]))
  list[[i]] <-vsum
}
library(gplots)
dataFrame <- as.data.frame(do.call(rbind, list)) 
#dataFrame <- t(dataFrame)
colnames(dataFrame) <- c("Name", "Value")
dataFrame$Value <- sapply(dataFrame$Value, as.numeric)
dataFrame <- dataFrame[sort(abs(dataFrame$Value),decreasing=F,index.return=T)[[2]],]
#lwid=c(0.1,5) #make column of dendrogram and key very small and other colum very big 
#lhei=c(0.1,5) #make row of key and other dendrogram very small and other row big. 
#heatmap.2(cbind(dataFrame$Value, dataFrame$Value), trace="n", Colv = NA, 
 #          dendrogram = "row", labCol = "", labRow = dataFrame$Name, cexRow = 0.75, lwid = lwid, lhei = lhei)
head(dataFrame, n =33)
