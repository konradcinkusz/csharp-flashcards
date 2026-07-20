\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{mybeamer}[2025/07/31 Custom beamer class]

\LoadClass{beamer}

\setbeamertemplate{navigation symbols}{
  \hyperlink{toc}{\beamerbutton{Contents}}\quad
  \insertslidenavigationsymbol
}

\setbeamertemplate{footline}{
  \leavevmode%
  \hbox{%
    \begin{beamercolorbox}[wd=\paperwidth,ht=2.5ex,dp=1ex,leftskip=1em,rightskip=1em]{author in head/foot}
      \scriptsize
      \href{https://github.com/konradcinkusz/CSharp-FlashCards-2025}{\faGithub\;CSharp-FlashCards}
    \end{beamercolorbox}%
  }
}

\RequirePackage{geometry}  
\RequirePackage[utf8]{inputenc}
\RequirePackage{xcolor}
\RequirePackage{multicol}
\RequirePackage{pgffor}
\RequirePackage{minted}
\RequirePackage{xparse}
\RequirePackage{tikz}
\usetikzlibrary{positioning,calc,arrows.meta} 
\RequirePackage{fontawesome5}
\RequirePackage{etoolbox}
\RequirePackage{listings}

\definecolor{MemoryColor}{HTML}{6BAED6}
\definecolor{OOPColor}{HTML}{FD8D3C}
\definecolor{MetaColor}{HTML}{9C27B0}
\definecolor{PerfColor}{HTML}{388E3C}
\definecolor{LangColor}{HTML}{0288D1}
\definecolor{ArchColor}{HTML}{795548}
\definecolor{LinqColor}{HTML}{8BC34A}
\definecolor{CollColor}{HTML}{D81B60}
\definecolor{AuthColor}{RGB}{155,89,182}
\definecolor{MicroColor}{HTML}{009688}
\definecolor{AIColor}{HTML}{2196F3}
\definecolor{AspNetColor}{HTML}{E91E63}
\definecolor{BlazorColor}{HTML}{673AB7}
\definecolor{AspireColor}{HTML}{00BCD4}
\definecolor{DbColor}{HTML}{FF5722}
\definecolor{DockerColor}{HTML}{1D63ED}
\definecolor{CICDColor}{HTML}{607D8B}
\definecolor{AzureColor}{HTML}{0078D4}
\definecolor{DDDColor}{HTML}{388E3C}
\definecolor{RestColor}{HTML}{FF9800}
\definecolor{AiToolColor}{HTML}{7B1FA2}
\definecolor{ToolingColor}{HTML}{795548}

\definecolor{CodeBg}{HTML}{F8F8F8}
\definecolor{sec1bg}{HTML}{6BAED6}  % C# Beginner
\definecolor{sec2bg}{HTML}{D81B60}  % C# Intermediate
\definecolor{sec3bg}{HTML}{9C27B0}  % C# Advanced
\definecolor{sec4bg}{HTML}{8BC34A}  % LINQ
\definecolor{sec5bg}{HTML}{388E3C}  % Threading
\definecolor{sec6bg}{HTML}{0288D1}  % EF
\definecolor{sec7bg}{HTML}{FD8D3C}  % Design Principles
\definecolor{sec8bg}{HTML}{795548}  % Design Patterns
\definecolor{sec9bg}{HTML}{795548}  % OAuth
\definecolor{sec10bg}{HTML}{009688} % Microservices
\definecolor{sec11bg}{HTML}{9B59B6} % Advanced Cloud & Leadership
\definecolor{sec12bg}{HTML}{9B59B6} % Azure Serverless
\definecolor{sec13bg}{HTML}{2196F3} % C# AI & .NET
\definecolor{sec14bg}{HTML}{E91E63} % ASP.NET Core
\definecolor{sec15bg}{HTML}{673AB7} % Blazor Server
\definecolor{sec16bg}{HTML}{00BCD4} % .NET Aspire
\definecolor{sec17bg}{HTML}{FF5722} % Databases
\definecolor{sec18bg}{HTML}{1D63ED} % Docker & Kubernetes
\definecolor{sec19bg}{HTML}{607D8B} % CI/CD & Terraform
\definecolor{sec20bg}{HTML}{0078D4} % Azure
\definecolor{sec21bg}{HTML}{388E3C} % DDD & CQRS
\definecolor{sec22bg}{HTML}{FF9800} % REST & SignalR
\definecolor{sec23bg}{HTML}{7B1FA2} % AI Tools & LLMs
\definecolor{sec24bg}{HTML}{E67E22} % Tooling & Agile

\setbeamercolor{sec1}{fg=white,bg=sec1bg}
\setbeamercolor{sec2}{fg=white,bg=sec2bg}
\setbeamercolor{sec3}{fg=white,bg=sec3bg}
\setbeamercolor{sec4}{fg=white,bg=sec4bg}
\setbeamercolor{sec5}{fg=white,bg=sec5bg}
\setbeamercolor{sec6}{fg=white,bg=sec6bg}
\setbeamercolor{sec7}{fg=white,bg=sec7bg}
\setbeamercolor{sec8}{fg=white,bg=sec8bg}
\setbeamercolor{sec9}{fg=white,bg=sec9bg}
\setbeamercolor{sec10}{fg=white,bg=sec10bg}
\setbeamercolor{sec11}{fg=white,bg=sec11bg}
\setbeamercolor{sec12}{fg=white,bg=sec12bg}
\setbeamercolor{sec13}{fg=white,bg=sec13bg}
\setbeamercolor{sec14}{fg=white,bg=sec14bg}
\setbeamercolor{sec15}{fg=white,bg=sec15bg}
\setbeamercolor{sec16}{fg=white,bg=sec16bg}
\setbeamercolor{sec17}{fg=white,bg=sec17bg}
\setbeamercolor{sec18}{fg=white,bg=sec18bg}
\setbeamercolor{sec19}{fg=white,bg=sec19bg}
\setbeamercolor{sec20}{fg=white,bg=sec20bg}
\setbeamercolor{sec21}{fg=white,bg=sec21bg}
\setbeamercolor{sec22}{fg=white,bg=sec22bg}
\setbeamercolor{sec23}{fg=white,bg=sec23bg}
\setbeamercolor{sec24}{fg=white,bg=sec24bg}

\lstset{
  basicstyle=\tiny\ttfamily,
  backgroundcolor=\color{CodeBg},
  numbers=left,
  numberstyle=\tiny,
  frame=single,
  framerule=0.3pt,
  framesep=2mm,
  breaklines
}

\setminted{
  fontsize=\scriptsize,
  linenos,
  bgcolor=CodeBg,
  frame=single,
  framerule=0.3pt,
  framesep=2mm,
  breaklines,
  breakanywhere=true,
  xleftmargin=10pt,
  autogobble=true
}

\AtBeginSection[]{
   \begin{frame}[allowframebreaks]{Outline}
    \small
    \tableofcontents[currentsection,hideothersubsections]
  \end{frame}
}