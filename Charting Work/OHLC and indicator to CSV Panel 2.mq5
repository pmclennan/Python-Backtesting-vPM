//+------------------------------------------------------------------+
//|                           OHLC and indicators to CSV Panel 2.mq5 |
//|                              Copyright © 2020, Vladimir Karputov |
//|                     https://www.mql5.com/ru/market/product/43516 |
//+------------------------------------------------------------------+
#property copyright "Copyright © 2020, Vladimir Karputov"
#property link      "https://www.mql5.com/ru/market/product/43516"
#property version   "2.002"
#include <Controls\Dialog.mqh>
#include <Controls\ListView.mqh>
#include <Controls\DatePicker.mqh>
#include <Controls\Button.mqh>
//--- input parameters
input string         InpFileName    = "001.csv";         // file name
input int            InpBuffer_0    = 0;                 // Buffer № ...
input double         InpEmptyVlaue  = 0.0;               // EMPTY_VALUE -> ...
//+------------------------------------------------------------------+
//| defines                                                          |
//+------------------------------------------------------------------+
//--- indents and gaps
#define INDENT_LEFT                         (11)      // indent from left (with allowance for border width)
#define INDENT_TOP                          (11)      // indent from top (with allowance for border width)
#define INDENT_RIGHT                        (11)      // indent from right (with allowance for border width)
#define INDENT_BOTTOM                       (11)      // indent from bottom (with allowance for border width)
#define CONTROLS_GAP_X                      (5)       // gap by X coordinate
#define CONTROLS_GAP_Y                      (5)       // gap by Y coordinate
//--- for list control
#define LIST_WIDTH                          (300)     // size by X coordinate
#define LIST_HEIGHT                         (70)      // size by Y coordinate
//--- for date picker controls
#define DATE_PICKER_WIDTH                   (150)     // size by X coordinate
#define DATE_PICKER_HEIGHT                  (20)      // size by Y coordinate
//--- for buttons
#define BUTTON_WIDTH                        (60)      // size by X coordinate
#define BUTTON_HEIGHT                       (20)      // size by Y coordinate
//+------------------------------------------------------------------+
//| Class CControlsDialog                                            |
//| Usage: main dialog of the Controls application                   |
//+------------------------------------------------------------------+
class CControlsDialog : public CAppDialog
  {
private:
   CListView         m_list_view;                     // CListView object
   CDatePicker       m_date_picker;                   // CDatePicker object
   CButton           m_button;                        // CButton object

public:
                     CControlsDialog(void);
                    ~CControlsDialog(void);
   //--- create
   virtual bool      Create(const long chart,const string name,const int subwin,const int x1,const int y1,const int x2,const int y2);
   //--- chart event handler
   virtual bool      OnEvent(const int id,const long &lparam,const double &dparam,const string &sparam);
   //--- fill ListView
   bool              FillListView(void);

protected:
   int               m_handles[];                     // array for storing indicator handles
   //--- create dependent controls
   bool              CreateListView(void);
   bool              CreateDatePicker(void);
   bool              CreateButton(void);
   //--- handlers of the dependent controls events
   void              OnChangeDataPicker(void);
   void              OnChangeListView(void);
   void              OnClickButton(void);

  };
//+------------------------------------------------------------------+
//| Event Handling                                                   |
//+------------------------------------------------------------------+
EVENT_MAP_BEGIN(CControlsDialog)
ON_EVENT(ON_CHANGE,m_date_picker,OnChangeDataPicker)
ON_EVENT(ON_CHANGE,m_list_view,OnChangeListView)
ON_EVENT(ON_CLICK,m_button,OnClickButton)
EVENT_MAP_END(CAppDialog)
//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CControlsDialog::CControlsDialog(void)
  {
  }
//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CControlsDialog::~CControlsDialog(void)
  {
  }
//+------------------------------------------------------------------+
//| Create                                                           |
//+------------------------------------------------------------------+
bool CControlsDialog::Create(const long chart,const string name,const int subwin,const int x1,const int y1,const int x2,const int y2)
  {
   ArrayFree(m_handles);
   if(!CAppDialog::Create(chart,name,subwin,x1,y1,x2,y2))
      return(false);
//--- create dependent controls
   if(!CreateListView())
      return(false);
   if(!CreateButton())
      return(false);
   if(!CreateDatePicker())
      return(false);
//--- succeed
   return(true);
  }
//+------------------------------------------------------------------+
//| Create the "ListView" element                                    |
//+------------------------------------------------------------------+
bool CControlsDialog::CreateListView(void)
  {
//--- coordinates
   int x1=INDENT_LEFT;
   int y1=INDENT_TOP;
   int x2=x1+LIST_WIDTH;
   int y2=y1+LIST_HEIGHT;
//--- create
   if(!m_list_view.Create(m_chart_id,m_name+"ListView",m_subwin,x1,y1,x2,y2))
      return(false);
   if(!Add(m_list_view))
      return(false);
   if(!FillListView())
      return(false);
//--- succeed
   return(true);
  }
//+------------------------------------------------------------------+
//| Create the "DatePicker" element                                  |
//+------------------------------------------------------------------+
bool CControlsDialog::CreateDatePicker(void)
  {
//--- coordinates
   int x1=INDENT_LEFT+LIST_WIDTH+CONTROLS_GAP_X;
   int y1=INDENT_TOP;
   int x2=x1+DATE_PICKER_WIDTH;
   int y2=y1+DATE_PICKER_HEIGHT;
//--- create
   if(!m_date_picker.Create(m_chart_id,m_name+"DatePicker",m_subwin,x1,y1,x2,y2))
      return(false);
   m_date_picker.Value(TimeTradeServer());
   if(!Add(m_date_picker))
      return(false);
//--- succeed
   return(true);
  }
//+------------------------------------------------------------------+
//| Create the "Start" buttom                                        |
//+------------------------------------------------------------------+
bool CControlsDialog::CreateButton(void)
  {
//--- coordinates
   int x1=INDENT_LEFT+LIST_WIDTH+CONTROLS_GAP_X;
   int y1=INDENT_TOP+DATE_PICKER_HEIGHT+CONTROLS_GAP_Y;
   int x2=x1+DATE_PICKER_WIDTH;
   int y2=y1+DATE_PICKER_HEIGHT;
//--- create
   if(!m_button.Create(m_chart_id,m_name+"Start",m_subwin,x1,y1,x2,y2))
      return(false);
   if(!m_button.Text("Start"))
      return(false);
   if(!Add(m_button))
      return(false);
//--- succeed
   return(true);
  }
//+------------------------------------------------------------------+
//| Fill "ListView" element                                          |
//+------------------------------------------------------------------+
bool CControlsDialog::FillListView(void)
  {
   ArrayFree(m_handles);
   m_list_view.ItemsClear();
//ChartRedraw(0);
//--- fill out with strings
   int windows_total=(int)ChartGetInteger(0,CHART_WINDOWS_TOTAL);
   for(int i=windows_total-1; i>=0; i--)
     {
      int indicators_total=ChartIndicatorsTotal(0,i);
      for(int j=indicators_total-1; j>=0; j--)
        {
         string indicator_name=ChartIndicatorName(0,i,j);
         int handle=ChartIndicatorGet(0,i,ChartIndicatorName(0,i,j));
         if(handle==INVALID_HANDLE)
            continue;
         int size=ArraySize(m_handles);
         ArrayResize(m_handles,size+1,10);
         m_handles[size]=handle;
         //Print("windows #",i,", indicator #",j,", ",indicator_name);
         if(!m_list_view.AddItem(indicator_name))
            return(false);
        }
     }
   m_list_view.Select(0);
//--- succeed
   return(true);
  }
//+------------------------------------------------------------------+
//| Event handler                                                    |
//+------------------------------------------------------------------+
void CControlsDialog::OnChangeDataPicker(void)
  {
   Comment(__FUNCTION__+" \""+TimeToString(m_date_picker.Value())+"\"");
  }
//+------------------------------------------------------------------+
//| Event handler                                                    |
//+------------------------------------------------------------------+
void CControlsDialog::OnChangeListView(void)
  {
   Comment(__FUNCTION__+" \""+m_list_view.Select()+"\"");
  }
//+------------------------------------------------------------------+
//| Event handler                                                    |
//+------------------------------------------------------------------+
void CControlsDialog::OnClickButton(void)
  {
   int value=(int)m_list_view.Value();
   Comment(__FUNCTION__+" \""+IntegerToString(value)+"\"");
   if(m_list_view.Value()>=ArraySize(m_handles))
      Comment(__FUNCTION__+" \"ERROR value: "+IntegerToString(value)+"\"");
   else
     {
      Comment(__FUNCTION__+" \"handle: "+IntegerToString(m_handles[value])+"\"");
      datetime start_time=m_date_picker.Value();
      datetime stop_time=TimeCurrent();
      MqlRates rates[];
      double values[];
      int copy_rates=CopyRates(Symbol(),Period(),start_time,stop_time,rates);
      int copy_values=CopyBuffer(m_handles[value],InpBuffer_0,start_time,stop_time,values);
      if(copy_rates!=copy_values)
        {
         Comment(__FUNCTION__+" \"CopyRates: "+IntegerToString(copy_rates)+", \"CopyBuffer: "+IntegerToString(copy_values));
         return;
        }
      //--- correct way of working in the "file sandbox"
      ResetLastError();
      int filehandle=FileOpen(InpFileName,FILE_WRITE|FILE_CSV);
      if(filehandle!=INVALID_HANDLE)
        {
         FileWrite(filehandle,"Date","Open","High","Low","Close","Buffer#0");
         for(int i=0; i<copy_rates; i++)
           {
            double buff_value=(values[i]==EMPTY_VALUE)?InpEmptyVlaue:values[i];
            FileWrite(filehandle,rates[i].time,
                      DoubleToString(rates[i].open,Digits()),
                      DoubleToString(rates[i].high,Digits()),
                      DoubleToString(rates[i].low,Digits()),
                      DoubleToString(rates[i].close,Digits()),
                      DoubleToString(buff_value,Digits()));
           }
         FileClose(filehandle);
         Comment(__FUNCTION__+" \"FileOpen OK\"");
        }
      else
         Comment(__FUNCTION__+" \"Operation FileOpen failed, error ",GetLastError());
     }
  }
//+------------------------------------------------------------------+
//| Global Variables                                                 |
//+------------------------------------------------------------------+
CControlsDialog ExtDialog;
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- create timer
   EventSetTimer(10);
//--- create application dialog
   if(!ExtDialog.Create(0,"OHLC and indicator to CSV Panel 2",0,40,40,525,160))
      return(INIT_FAILED);
//--- run application
   ExtDialog.Run();
//--- succeed
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
  {
//---
   ExtDialog.FillListView();
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
//---
   Comment("");
//--- destroy timer
   EventKillTimer();
//--- destroy dialog
   ExtDialog.Destroy(reason);
  }
//+------------------------------------------------------------------+
//| Expert chart event function                                      |
//+------------------------------------------------------------------+
void OnChartEvent(const int id,         // event ID
                  const long& lparam,   // event parameter of the long type
                  const double& dparam, // event parameter of the double type
                  const string& sparam) // event parameter of the string type
  {
   ExtDialog.ChartEvent(id,lparam,dparam,sparam);
  }
//+------------------------------------------------------------------+
