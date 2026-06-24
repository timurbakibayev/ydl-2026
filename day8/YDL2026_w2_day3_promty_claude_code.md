# YDL 2026, Week 2, Day 3. Claude Code prompts (team task)

Use these prompts one step at a time. Run and read the output before moving
to the next prompt. Do not trust a metric until you have looked at the plot
behind it.

## Step 1. EDA and scaling

```
Load the dataset from <path>. Show shape, dtypes, the first rows, summary
statistics, missing-value counts per column, and a correlation matrix as a
heatmap. Plot a histogram for every numeric feature. Tell me which features
are on very different scales. Then create a StandardScaler-transformed copy
of the numeric features and keep both the raw and scaled versions.
```

## Step 2. Clustering with kmeans

```
On the scaled features, run kmeans for k from 2 to 10. Plot the elbow curve
(inertia vs k) and the silhouette score vs k on two separate charts.
Recommend a value of k and explain the trade-off in one short paragraph.
Do not pick k automatically without showing both plots.
```

## Step 3. Create the prediction column

```
Fit kmeans with the chosen k on the scaled features and add the cluster
label as a new column called cluster in the original dataframe. For each
cluster, show the mean of every feature so I can describe what makes each
group different. Suggest a short human-readable name for each cluster based
on its feature means.
```

## Step 4. PCA for visual check

```
Run PCA on the scaled features and reduce to 2 components. Scatter-plot the
objects on PC1 vs PC2, colored by the cluster column from step 3. Print how
much variance each of the 2 components explains and the total. Tell me
whether the clusters look separated or overlapping in this 2D projection.
```

## Step 5. Classification on the new label

```
Using the original features as input and the cluster column as the target,
split into train and test sets. Train a logistic regression and a KNN
classifier. Report accuracy, precision, recall, and F1 on both train and
test. Show the confusion matrix for the better model. Tell me whether the
classifier learns the cluster boundaries well, and what that says about
whether the clusters are real.
```
