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
  vsum <-append(vsum, sum(abs(vector)))
  list[[i]] <-vsum
}
dataFrame <- as.data.frame(do.call(rbind, list)) 
#dataFrame <- t(dataFrame)
colnames(dataFrame) <- c("Name", "Value")
dataFrame$Value <- sapply(dataFrame$Value, as.numeric)
dataFrame <- dataFrame[sort(abs(dataFrame$Value),decreasing=F,index.return=T)[[2]],]
#lwid=c(0.1,5) #make column of dendrogram and key very small and other colum very big 
#lhei=c(0.1,5) #make row of key and other dendrogram very small and other row big. 
#heatmap.2(cbind(dataFrame$Value, dataFrame$Value), trace="n", Colv = NA, 
 #          dendrogram = "row", labCol = "", labRow = dataFrame$Name, cexRow = 0.75, lwid = lwid, lhei = lhei)
#heatmap.2(cbind(dataFrame$Value, dataFrame$Value), trace="n", Colv = NA, 
#          dendrogram = "row", labCol = "", labRow = dataFrame$Name, cexRow = 0.75, lwid = lwid, lhei = lhei)
std <- read.csv(file= '/nas/longleaf/home/jyhh/AllSTD_MASK_NO_WEIGHT_WM_Seg_median.csv')
numAll <-ncol(std)-2
numSamples <- nrow(std)
list <- list()
for (i in 1:numSamples){
  vector <- vector()
  for (j in 1:numAll){
    value <- std[i,j+2]
    vector <- append(vector, value)
    
  }
  vsum <- vector()
  vsum <-append(vsum, sub(".*sepLabel_", "", std[i,1]))
  vsum <-append(vsum, sum(abs(vector)))
  list[[i]] <-vsum
}
dataFrame1 <- as.data.frame(do.call(rbind, list)) 
#dataFrame <- t(dataFrame)
colnames(dataFrame1) <- c("Name", "Value")
dataFrame1$Value <- sapply(dataFrame1$Value, as.numeric)
dataFrame1 <- dataFrame1[sort(abs(dataFrame1$Value),decreasing=F,index.return=T)[[2]],]
#lwid=c(0.1,5) #make column of dendrogram and key very small and other colum very big 
#lhei=c(0.1,5) #make row of key and other dendrogram very small and other row big. 
#heatmap.2(cbind(dataFrame$Value, dataFrame$Value), trace="n", Colv = NA, 
#          dendrogram = "row", labCol = "", labRow = dataFrame$Name, cexRow = 0.75, lwid = lwid, lhei = lhei)
df_merge <- merge(dataFrame1,dataFrame,by="Name")
df_merge$Top10IL <- ifelse(df_merge$Value.y >= quantile(df_merge$Value.y, probs = 0.9), TRUE, FALSE)
df_merge$Top10STD <- ifelse(df_merge$Value.x >= quantile(df_merge$Value.x, probs = 0.9), TRUE, FALSE)
both_good <-subset(df_merge, subset=(Top10STD==TRUE&Top10IL==TRUE))


