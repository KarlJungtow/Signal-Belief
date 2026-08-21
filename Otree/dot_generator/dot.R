rm(list = ls())

library(ggplot2)

## where to save files
setwd("C:/Users/Bulutay/Documents/GitHub/Signal-Belief/Otree/dot_generator")

#######################
## PARAMETERS YOU SET ##
#######################

# treatments (edit this as needed)
treatments <- c("A", "B", "C")   # e.g. c("baseline", "tax", "subsidy")

# grid size (20x20)
grid_size   <- 20
n_cells     <- grid_size^2

# desired red-dot counts
red_counts <- c(120, 190, 195, 199, 201, 205, 210, 280)  # example; include others as needed

# special red counts that get a/b suffix
special_counts <- c(120, 280)

##########################
## PREPARE COORDINATES  ##
##########################

xaxisa <- rep(1:grid_size, times = grid_size)
yaxisa <- rep(1:grid_size, each  = grid_size)

##########################
## GENERATE & SAVE PLOTS##
##########################

name   <- c()
number <- c()

set.seed(123)

for (treat in treatments) {
  for (num_red in red_counts) {
    
    if (num_red > n_cells) {
      stop(paste("Requested", num_red, "red dots, but grid has only", n_cells, "cells."))
    }
    
    # case 1: special counts (120, 280) → x1_a, x1_b, x2_a, x2_b
    if (num_red %in% special_counts) {
      xs       <- c("x1", "x2")
      suffixes <- c("a", "b")
      
      for (x in xs) {
        for (suf in suffixes) {
          
          # build dot colors
          colorito <- c(rep(1, num_red), rep(0, n_cells - num_red))
          colorito <- sample(colorito, size = n_cells, replace = FALSE)
          
          example <- data.frame(
            xaxisa   = xaxisa,
            yaxisa   = yaxisa,
            colorito = as.factor(colorito)
          )
          
          p <- ggplot(data = example, aes(x = xaxisa, y = yaxisa, color = colorito)) +
            theme_bw() +
            theme(
              axis.title.x    = element_blank(),
              axis.text.x     = element_blank(),
              axis.ticks.x    = element_blank(),
              axis.title.y    = element_blank(),
              axis.text.y     = element_blank(),
              axis.ticks.y    = element_blank(),
              legend.position = "none",
              panel.grid.major = element_blank(),
              panel.grid.minor = element_blank(),
              panel.background = element_blank(),
              axis.line        = element_line(colour = "black")
            ) +
            scale_color_manual(breaks = c("0", "1"), values = c("blue", "red")) +
            geom_point(size = 5)
          
          # dots_{treatment}_{r}_{x}_{suffix}.png
          fname <- sprintf("dots_%s_%d_%s_%s.png", treat, num_red, x, suf)
          
          ggsave(
            filename = fname,
            plot     = p,
            width    = 20,
            height   = 20,
            units    = "cm"
          )
          
          number <- append(number, num_red)
          name   <- append(name, gsub("\\.png$", "", fname))
        }
      }
      
    } else {
      # case 2: all other counts → x1, x2 (no a/b)
      xs <- c("x1", "x2")
      
      for (x in xs) {
        
        colorito <- c(rep(1, num_red), rep(0, n_cells - num_red))
        colorito <- sample(colorito, size = n_cells, replace = FALSE)
        
        example <- data.frame(
          xaxisa   = xaxisa,
          yaxisa   = yaxisa,
          colorito = as.factor(colorito)
        )
        
        p <- ggplot(data = example, aes(x = xaxisa, y = yaxisa, color = colorito)) +
          theme_bw() +
          theme(
            axis.title.x    = element_blank(),
            axis.text.x     = element_blank(),
            axis.ticks.x    = element_blank(),
            axis.title.y    = element_blank(),
            axis.text.y     = element_blank(),
            axis.ticks.y    = element_blank(),
            legend.position = "none",
            panel.grid.major = element_blank(),
            panel.grid.minor = element_blank(),
            panel.background = element_blank(),
            axis.line        = element_line(colour = "black")
          ) +
          scale_color_manual(breaks = c("0", "1"), values = c("blue", "red")) +
          geom_point(size = 5)
        
        # dots_{treatment}_{r}_{x}.png
        fname <- sprintf("dots_%s_%d_%s.png", treat, num_red, x)
        
        ggsave(
          filename = fname,
          plot     = p,
          width    = 20,
          height   = 20,
          units    = "cm"
        )
        
        number <- append(number, num_red)
        name   <- append(name, gsub("\\.png$", "", fname))
      }
    }
  }
}

# quick check
print(getwd())
print(list.files(pattern = "^dots_.*\\.png$"))
