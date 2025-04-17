### Shiny App ###
library(shiny)
library(shinydashboard)
library(tidyverse)
library(ggthemes)
#install.packages("shinyWidgets")
library(shinyWidgets)
library(viridis)
library(stringr)
library(DT)

# Read data
filtered_data <- read.csv("top8_mayoral.csv", stringsAsFactors = FALSE)

# UI
ui <- dashboardPage(
  dashboardHeader(title = "Top 8 Mayoral Candidate Campaign Finance Data"),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Type Breakdown",     tabName = "cf_breakdown",     icon = icon("bar-chart")),
      menuItem("Top Donors", tabName = "top_donors", icon = icon("users")),
      menuItem("Contributions & Expenditures", tabName = "timeline", icon = icon("line-chart"))
    )
    ),
  dashboardBody(
    tabItems(
      tabItem(
        tabName = "cf_breakdown",
        fluidRow(
          box(
            title = "Select Candidates",
            status = "primary",
            solidHeader = TRUE,
            width = 12,
            checkboxGroupButtons(
              inputId = "candidate_select",
              label = NULL,
              choices = sort(unique(filtered_data$Cand.Committee.)),
              selected = sort(unique(filtered_data$Cand.Committee.)),
              direction = "horizontal",
              justified = TRUE,
              status = "info",
              size = "sm",
              checkIcon = list(
                yes = icon("check-circle"),
                no = icon("circle")
              )
            )
          )
        ),
        fluidRow(
          box(
            title = "Total $ by Campaign Finance Category",
            status = "primary",
            solidHeader = TRUE,
            width = 12,
            plotOutput("cfTypeChart", height = "650px")
          )
        )
      ),
      tabItem(
        tabName = "top_donors",
        fluidRow(
          box(
            title = "Top Donors by Candidate",
            status = "primary",
            solidHeader = TRUE,
            width = 12,
            dataTableOutput("topDonorsTable")
          )
        )
      ),
      tabItem(
        tabName = "timeline",
        fluidRow(
          box(
            title = "Select Candidates", status = "primary", solidHeader = TRUE,
            width = 12,
            checkboxGroupButtons(
              inputId = "timeline_candidate",
              label=NULL,
              choices = sort(unique(filtered_data$Cand.Committee.)),
              selected = sort(unique(filtered_data$Cand.Committee.)),
              direction = "horizontal",
              justified = TRUE,
              status = "info",
              size = "sm",
              checkIcon = list(yes=icon("check-circle"),
                               no=icon("circle")
                               )
            )
          )
        ),
        fluidRow(
          box(
            title       = "Show:",
            status      = "primary",
            solidHeader = TRUE,
            width       = 12,
            shinyWidgets::radioGroupButtons(
              inputId   = "timeline_metric",
              label     = NULL,
              choices   = c("Contributions", "Expenditures"),
              selected  = "Contributions",
              justified = TRUE,
              status    = "warning",
              size      = "sm"
            )
          )
        ),
        fluidRow(
          box(
            title = "Contributions & Expenditures",
            status = "primary",
            solidHeader = TRUE,
            width = 12,
            plotOutput("timelineChart", height = "600px")
          )
        )
      )
    )
  )
)

# Server
server <- function(input, output, session) {
  output$cfTypeChart <- renderPlot({
    req(input$candidate_select)
    
    cf_data <- filtered_data %>%
      filter(Cand.Committee. %in% input$candidate_select) %>%
      group_by(Cand.Committee., CF_Type) %>%
      summarise(total_amount = sum(Amount_num, na.rm = TRUE), .groups = "drop")
    
    ggplot(cf_data, aes(
      x = Cand.Committee.,
      y = total_amount,
      fill = CF_Type
    )) +
      geom_bar(stat = "identity", position = position_dodge(width = 0.8)) +
      scale_y_continuous(
        labels = scales::dollar_format(prefix = "$", big.mark = ","),
        expand = expansion(mult = c(0,0.05))
      ) +
      labs(
        title = "Total $ By Campaign Finance Category",
        subtitle = "As of April 15, 2025",
        x = "Candidate",
        y = "Total Contributions ($)",
        fill = "Category Type"
      ) +
      theme_fivethirtyeight()+
      scale_fill_brewer(palette = "Dark2") +
      theme(axis.text.x = element_text(angle = 45, hjust = 1),
            plot.title = element_text(hjust = 0.5))
  })
  
  ### Donor Table ###
  output$topDonorsTable <- DT::renderDataTable({
    donor_summary <- filtered_data %>%
      filter(Contact.Type. == "Contributor") %>%
      mutate(
        donor_name = str_trim(
          str_extract(Name., "^[^0-9]+")
        )
      ) %>%
      group_by(Cand.Committee., donor_name) %>%
      summarise(
        total_amount = sum(Amount_num, na.rm = TRUE),
        .groups = "drop"
      ) %>%
      group_by(Cand.Committee.) %>%
      slice_max(order_by = total_amount, n=10, with_ties = FALSE) %>%
      ungroup() %>%
      arrange(Cand.Committee., desc(total_amount))
    
    # Render as DT
    DT::datatable(
      donor_summary,
      rownames = FALSE,
      extensions = "RowGroup",
      options = list(paging = FALSE, scollY="600px",
                     rowGroup = list(dataSrc=0),
                     columnDefs = list(list(visible=FALSE, targets=0))),
      colnames = c("Candidate", "Donor", "Total Contributed")
    ) %>%
      formatCurrency(
        columns = "total_amount",
        currency = "$",
        digits = 0
      )
  })
  
  ### Contributions v Expenditures
  output$timelineChart <- renderPlot({
    sel <- input$timeline_candidate
    if (is.null(sel) || length(sel)==0) {
      sel <- unique(filtered_data$Cand.Committee.)
    }
    
    # 2. Map the toggle to our category values
    cat_map <- if (input$timeline_metric == "Contributions") "Contribution" else "Expenditure"
    
    # 3. Prepare cumulative monthly data (both categories)
    df <- filtered_data %>%
      filter(Cand.Committee. %in% sel) %>%
      mutate(trans_dt = parse_date_time(TransDate., orders = "mdy IMS p")) %>%
      filter(
        CF_Type == "Monetary Political Contributions" |
          CF_Type %in% c(
            "Political Expenditures Made From Personal Funds",
            "Political Expenditures Made From Political Contributions"
          )
      ) %>%
      mutate(
        category    = if_else(
          CF_Type == "Monetary Political Contributions",
          "Contribution",
          "Expenditure"
        ),
        trans_month = as.Date(floor_date(trans_dt, "month"))
      ) %>%
      group_by(Cand.Committee., trans_month, category) %>%
      summarise(monthly_amount = sum(Amount_num, na.rm = TRUE), .groups = "drop") %>%
      arrange(Cand.Committee., category, trans_month) %>%
      group_by(Cand.Committee., category) %>%
      mutate(cumulative_amount = cumsum(monthly_amount)) %>%
      ungroup()
    
    # 4. Filter to only the chosen metric
    plot_df <- df %>% filter(category == cat_map)
    
    # 5. Plot
    ggplot(plot_df,
           aes(x = trans_month, y = cumulative_amount, color = Cand.Committee.)) +
      geom_line(size = 1) +
      geom_point(size = 2) +
      scale_x_date(
        date_breaks = "1 month",
        date_labels = "%b %Y",
        expand      = expansion(add = c(0, 0))
      ) +
      scale_y_continuous(
        labels = scales::dollar_format(prefix = "$", big.mark = ","),
        expand = expansion(mult = c(0, 0.05))
      ) +
      labs(
        title = paste(input$timeline_metric, "Cumulative by Month"),
        x     = "Month",
        y     = "Cumulative Amount ($)",
        color = "Candidate"
      ) +
      theme_fivethirtyeight() +
     # scale_color_economist() +
      theme(
        axis.text.x     = element_text(angle = 45, hjust = 1),
        plot.title      = element_text(hjust = 0.5, size = 16),
        legend.position = "bottom",
        plot.margin     = unit(c(0.5, 0.5, 0.5, 0.5), "cm")
      )

  })
}

shinyApp(ui, server)
