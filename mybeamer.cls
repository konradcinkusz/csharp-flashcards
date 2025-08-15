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

\definecolor{CodeBg}{HTML}{F8F8F8} 
\definecolor{sec1bg}{HTML}{6BAED6}  % C# Beginner – MemoryColor
\definecolor{sec2bg}{HTML}{D81B60}  % C# Intermediate – CollColor
\definecolor{sec3bg}{HTML}{9C27B0}  % C# Advanced – MetaColor
\definecolor{sec4bg}{HTML}{8BC34A}  % LINQ – LinqColor
\definecolor{sec5bg}{HTML}{388E3C}  % Threading – PerfColor
\definecolor{sec6bg}{HTML}{0288D1}  % EF – LangColor
\definecolor{sec7bg}{HTML}{FD8D3C}  % Design Principles – OOPColor
\definecolor{sec8bg}{HTML}{795548}  % Design Patterns – ArchColor
\definecolor{sec9bg}{HTML}{795548}  % Design Patterns – ArchColor
\definecolor{sec10bg}{HTML}{9B59B6} % Advanced Cloud & Leadership – AuthColor

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