import PySimpleGUI as sg
import math
import datetime

def keyexpr(s, key, defval=None):
    ret = defval
    p1 = s.find(key + "(")
    if p1 == 0 or p1 > 0 and s[p1-1] in " ,":
        p2 = s.find(")", p1)
        if p2 >= 0:
            return s[p1 + len(key) + 1 : p2]
    p1 = s.find(key + "=")
    if p1 == 0 or p1 > 0 and s[p1-1] in " ,":
        s = s[p1 + len(key) + 1:]
        c = s[:1]
        if c in "'\"":
            p2 = s.find(c, 1)
            if p2 >= 0:
                return s[1 : p2]
        else:
            s = s.replace(",", " ") + " "
            return s[: s.find(" ")]
    return ret

def canvasinit(graph):
    graph.canvasw = max(graph.TKCanvas.winfo_width(), graph.TKCanvas.winfo_reqwidth())
    graph.canvash = max(graph.TKCanvas.winfo_height(), graph.TKCanvas.winfo_reqheight())
    graph.canvascolor = graph.TKCanvas["bg"]
    graph.font1 = "Any " + str(int(round(7 + graph.canvash / 100, 0)))
    graph.font2 = "Any " + str(int(round(14 + graph.canvash / 50, 0)))
    graph.fontmsg = "Any " + str(int(round(18 + graph.canvash / 30, 0)))
    if not hasattr(graph, "linecolor"):                     # first run
        graph.linecolor = sg.theme_input_background_color() \
            if graph.canvascolor == sg.theme_background_color() \
            else sg.theme_background_color()
        graph.textcolor = sg.theme_input_text_color()
    return


def figwidth(font, txt):
    return sg.Text.string_width_in_pixels(font, txt)

def figheight(font):
    return sg.Text.char_height_in_pixels(font)

def figsize(font, txt):
    return figwidth(font, txt), figheight(font)


def message(graph, msg, color="black"):

    if isinstance(msg, str):
        msgarr = [msg]
    elif isinstance(msg, tuple):
        msgarr = msg
    else:
        msgarr = msg.copy()
    if isinstance(color, str):
        colarr = [color for _ in range(len(msgarr))]
    elif isinstance(color, tuple):
        colarr = color
    else:
        colarr = color.copy()

    fontsize = int(graph.fontmsg.split()[1])
    linespace = int(round(fontsize / 8, 0))
    lineheight = figheight(graph.fontmsg)

    graph.erase()

    x = graph.canvasw / 2
    textheight = len(msgarr) * (lineheight + linespace) - linespace
    y = graph.canvash - (graph.canvash - textheight) / 2
    for i, m in enumerate(msgarr):
        colitem = colarr[i].split("/")
        colitem.reverse()
        xvar, yvar = x, y
        for c in colitem:
            graph.draw_text(m, (xvar, yvar), font=graph.fontmsg, color=c.strip(),
                            text_location=sg.TEXT_LOCATION_TOP)
            xvar -= 2
            yvar += 2
        y -= (lineheight + linespace)
    return


class ColChart(sg.Graph):
    def activate(self, title, labels, data, comments, **kwargs):
        canvasinit(self)
        if len(labels) == 0 or len(data) == 0 or len(labels) != len(data):
            self.proper = False
            return
        self.proper = True
        self.MARGIN = kwargs["margin"] if "margin" in kwargs else 10
        self.comments = comments
        self.last_index = -1
        self.last_box = -1
        self.infofig = -1
        color = ("red", "green", "blue", "orange", "yellow", "turquoise3",
                 "gold2", "grey", "dark red", "lime green", "magenta2", "purple1")

        dfix = [(d,) for d in data] if isinstance(data[0], (float, int)) else data.copy()
        self.grouplen = len(dfix[0])
        self.commentwidth = figwidth(self.font1, " " + max(comments, key=len) + " ")

        minval = min(map(min, dfix))
        maxval = max(map(max, dfix))

        self.colparam = []
        for i, dt in enumerate(dfix):
            dict = {"label": labels[i], "textfig": -1}
            c = 0
            for g in range(self.grouplen):
                dict["value" + str(g)] = dt[g]
                dict["color" + str(g)] = color[c]
                dict["figure" + str(g)] = -1
                c = 0 if c == len(color) - 1 else c + 1
            self.colparam.append(dict)

        # calibrating text sizes
        self.text1h = figheight(self.font1)
        self.text2h = figheight(self.font2)

        bottom = max(self.text1h + 2, self.MARGIN)
        if minval < 0:
            axis = bottom + (self.canvash - self.MARGIN - bottom) \
                   * abs(minval) / (maxval - minval)
        else:
            axis = bottom
        positive = self.canvash - self.MARGIN - axis
        negative = axis - bottom

        self.erase()

        # drawing title
        if title == "":
            self.chartx1 = self.MARGIN
        else:
            temp = self.draw_text(title, (0, self.MARGIN),
                                  font=self.font2, color=self.textcolor, angle=90,
                                  text_location=sg.TEXT_LOCATION_TOP_LEFT)
            self.chartx1 = self.get_bounding_box(temp)[1][0] + self.MARGIN
        self.chartx2 = self.canvasw - self.MARGIN

        # gridlines
        step = 20
        for y in range(int(axis), self.canvash - self.MARGIN + 1, step):
            self.draw_line((self.chartx1, y), (self.chartx2, y), color=self.linecolor)
        for y in range(int(axis), int(bottom) - 1, -step):
            self.draw_line((self.chartx1, y), (self.chartx2, y), color=self.linecolor)
        # axis if there are negative values
        if axis != bottom:
            temp = self.draw_line((self.chartx1, axis), (self.chartx2, axis),
                                  color=self.linecolor, width=5)
            self.TKCanvas.itemconfig(temp, dash=(5,))

        # drawing columns
        elements = len(self.colparam)
        self.halfbar = (self.chartx2 - self.chartx1) / ((self.grouplen * 2 + 1) * elements - 1)
        posl = self.chartx1
        labelx = self.chartx1 + self.halfbar * self.grouplen
        for cp in self.colparam:
            for g in range(self.grouplen):
                value = cp["value" + str(g)]
                if value < 0:
                    post = axis - negative * value / minval
                else:
                    post = axis + positive * value / maxval
                cp["figure"+str(g)] = self.draw_rectangle((posl, post),
                                            (posl + self.halfbar * 2, axis),
                                             fill_color=cp["color"+str(g)])
                posl += self.halfbar * 2
            posl += self.halfbar
            cp["textfig"] = self.draw_text(cp["label"], (labelx, 1),
                                           font=self.font1, color=self.textcolor,
                                           text_location=sg.TEXT_LOCATION_BOTTOM)
            labelx += self.halfbar * (self.grouplen * 2 + 1)

        self.figlist = [[cp["figure" + str(g)] for cp in self.colparam] for g in range(self.grouplen)]
        self.textlist = [cp["textfig"] for cp in self.colparam]
        return

    def _clicked_item(self, loc):
        k = -1
        figs = self.get_figures_at_location(loc)
        if self.infofig in figs:
            k = self.last_index
        elif len(figs) > 0:
            for f in figs:
                if f in self.textlist:
                    k = self.textlist.index(f)
                    break
            else:
                for g in range(self.grouplen):
                    if figs[0] in self.figlist[g]:
                        k = self.figlist[g].index(figs[0])
                        break
        return k

    def _label_box(self, textfig):
        box1, box2 = self.get_bounding_box(textfig)
        box_figid = self.draw_rectangle(box1, box2, fill_color="black")
        self.TKCanvas.itemconfig(textfig, fill="white")
        self.bring_figure_to_front(textfig)
        return box_figid

    def handler(self, event, values):
        if not self.proper:
            return None

        k = self._clicked_item(values[event])
        if k < 0:
            return None
        cpitem = self.colparam[k]

        if self.last_box >= 0:
            self.delete_figure(self.last_box)
            self.TKCanvas.itemconfig(self.colparam[self.last_index]["textfig"], fill=self.textcolor)
        if self.infofig >= 0:
            for i in range(self.grouplen * 3 + 1):
                self.delete_figure(self.infofig + i)

        if k == self.last_index:
            self.last_index = self.infofig = -1
            retindex = -k
        else:
            retindex = k
            self.last_box = self._label_box(cpitem["textfig"])
            self.last_index = k
            #------------- text info ---------------------
            valstr = [" {:,}".format(cpitem["value" + str(g)]) for g in range(self.grouplen)]
            vw = figwidth(self.font1, max(valstr, key=len))

            if k + 1 > len(self.colparam) / 2:
                x1 = self.chartx1
                x2 = x1 + self.commentwidth + vw + 10
            else:
                x2 = self.chartx2
                x1 = x2 - self.commentwidth - vw - 10

            linespace = 2
            y1 = self.canvash - self.MARGIN
            y2 = y1 - 10 - self.text1h * self.grouplen - linespace * (self.grouplen - 1)
            y = y1 - 5
            self.infofig = self.draw_rectangle((x1, y1), (x2, y2),
                                               fill_color="black", line_color="white")
            for g in range(self.grouplen):
                txt = " " + self.comments[g] + " "
                self.draw_rectangle((x1 + 5, y), (x1 + 5 + self.commentwidth, y - self.text1h),
                                    fill_color=cpitem["color" + str(g)])
                self.draw_text(txt, (x1 + 5, y),
                               font=self.font1, color="white",
                               text_location=sg.TEXT_LOCATION_TOP_LEFT)
                txt = "{:,}".format(cpitem["value" + str(g)])
                self.draw_text(txt, (x2 - 5, y), font=self.font1,
                               text_location=sg.TEXT_LOCATION_TOP_RIGHT, color="white")
                y -= (self.text1h + linespace)

        return retindex


class LineChart(sg.Graph):

    def draw_options(self, width1, width2, point, circler, circlew):
        self.width1, self.width2 = width1, width2
        self.point = point * 2          # from radius to diameter
        self.circler, self.circlew = circler, circlew
        return

    def activate(self, title="", *args, **kwargs):

        def calc_y(value):
            if value < 0:
                ypos = axis - negative * value / minval
            else:
                ypos = axis + positive * value / maxval
            return ypos

        labels = [a[0] for a in args]
        datelist = [a[1] for a in args]
        datalist = [a[2] for a in args]
        options = [("" if len(a) < 4 else a[3]) for a in args]

        canvasinit(self)
        if len(args) == 0 or list(map(len, datelist)) != list(map(len, datalist)):
            self.proper = False
            return
        self.proper = True
        if not hasattr(self, "width1"):        # draw_options() was not called before
            self.width1, self.width2 = 2, 3
            self.point = 8
            self.circler, self.circlew = 6, 3
        self.MARGIN = kwargs["margin"] if "margin" in kwargs else 10
        self.dt1 = min(map(min, datelist))
        self.dt2 = max(map(max, datelist))
        self.labels = labels
        self.wholeperiod = self._period(self.dt1, self.dt2)
        self.point_index = self.markline = -1
        self.pointfigs = []
        self.linefigs = []
        self.infofigs = []
        minval = min(map(min, datalist))
        maxval = max(map(max, datalist))
        # --------- chart -----------------------
        self.datewidth, self.text1h = figsize(self.font1, "XXXX-XX-XX")
        self.valuewidth = figwidth(self.font1, "{:+,}".format(int(maxval)))
        self.text2h = figheight(self.font2)

        bottomtop = int(max(self.text1h + 2, self.MARGIN))
        workheight = self.canvash - bottomtop * 2
        if minval < 0:
            axis = bottomtop + workheight * abs(minval) / (maxval - minval)
        else:
            axis = bottomtop
        positive = self.canvash - bottomtop - axis
        negative = axis - bottomtop
        self.bottomtop = bottomtop
        self.axis = axis
        self.tolerance = (maxval - min(minval, 0)) / workheight

        self.erase()

        # drawing title
        if title == "":
            self.chartx1 = self.MARGIN
        else:
            temp = self.draw_text(title, (0, self.MARGIN),
                                  font=self.font2, color=self.textcolor, angle=90,
                                  text_location=sg.TEXT_LOCATION_TOP_LEFT)
            self.chartx1 = self.get_bounding_box(temp)[1][0] + self.MARGIN
        self.chartx2 = self.canvasw - self.MARGIN
        workwidth = self.chartx2 - self.chartx1

        # gridlines
        step = 20
        for y in range(int(axis), self.canvash - bottomtop + 1, step):
            self.draw_line((self.chartx1, y), (self.chartx2, y), color=self.linecolor)
        for y in range(int(axis), bottomtop - 1, -step):
            self.draw_line((self.chartx1, y), (self.chartx2, y), color=self.linecolor)
        # axis if there are negative values
        if axis != bottomtop:
            temp = self.draw_line((self.chartx1, axis), (self.chartx2, axis),
                                  color=self.linecolor, width=5)
            self.TKCanvas.itemconfig(temp, dash=(5,))

        color = ("red", "blue", "green", "orange", "yellow", "turquoise1", "saddle brown",
                 "MediumPurple1", "dim gray", "dodger blue", "lawn green", "magenta2")

        c = 0
        for elem in range(len(datalist)):
            elemshape = keyexpr(options[elem], "shape", "")   # may contain <p>oints, <s>tepped, <d>ashed
            elemcolor = keyexpr(options[elem], "color")
            datainner = datalist[elem]
            dateinner = datelist[elem]
            figcolor = color[c] if elemcolor is None else elemcolor
            tsize = workwidth / len(labels)
            px = self.chartx1 + c * tsize + tsize / 2
            labfig = self.draw_text(labels[c], (px, 0), color=figcolor, font=self.font1,
                                    text_location=sg.TEXT_LOCATION_BOTTOM)
            px = self.chartx1 + workwidth * self._period(self.dt1, dateinner[0]) / self.wholeperiod
            py = calc_y(datainner[0])
            prevx, prevy, prevdt = px, py, dateinner[0]
            if "p" in elemshape:
                pfig = self.draw_point((px, py), size=self.point, color=figcolor)
                self.pointfigs.append((pfig, datainner[0], dateinner[0], figcolor, elem))

            linepoints = [(prevx, prevy)]
            for i in range(1, len(datainner)):
                dt = dateinner[i]
                dd = datainner[i]
                px += workwidth * self._period(prevdt, dt) / self.wholeperiod
                if "s" in elemshape:
                    linepoints.append((px, calc_y(datainner[i - 1])))
                    py = calc_y(dd)
                else:
                    py = calc_y(dd)
                linepoints.append((px, py))
                if "p" in elemshape:
                    pfig = self.draw_point((px, py), size=self.point, color=figcolor)
                    self.pointfigs.append((pfig, dd, dt, figcolor, elem))
                prevx, prevy, prevdt = px, py, dt
            linefig = self.draw_lines(linepoints, color=figcolor, width=self.width1)
            if "d" in elemshape:
                self.TKCanvas.itemconfig(linefig, dash=(1,))
            self.linefigs.append({"label": labfig, "line": linefig})
            c = 0 if c == len(color) - 1 else c + 1

        # left-right arrows
        if len(self.pointfigs) == 0:
            self.arrow_l = self.arrow_r = -1
        else:
            x = self.chartx1 - self.MARGIN
            self.arrow_l = self.draw_text(sg.SYMBOL_LEFT_DOUBLE, (x,0),
                           font=self.fontmsg, color=self.textcolor,
                           text_location=sg.TEXT_LOCATION_BOTTOM_LEFT)
            x = self.chartx2 + self.MARGIN
            self.arrow_r = self.draw_text(sg.SYMBOL_RIGHT_DOUBLE, (x,0),
                           font=self.fontmsg, color=self.textcolor,
                           text_location=sg.TEXT_LOCATION_BOTTOM_RIGHT)

    def _period(self, dt1, dt2):
        delta = dt2 - dt1
        return delta.days

    def _info_location(self, x, w):
        if x + w / 2 > self.chartx2:
            tloc = sg.TEXT_LOCATION_TOP_RIGHT
        elif x - w / 2 < self.chartx1:
            tloc = sg.TEXT_LOCATION_TOP_LEFT
        else:
            tloc = sg.TEXT_LOCATION_TOP
        return tloc

    def _addinfo(self, fig):
        self.infofigs.append(fig)
        return

    def _clearinfo(self):
        for fig in self.infofigs:
            self.delete_figure(fig)
        self.infofigs = []
        if self.markline >= 0:
            lp = self.linefigs[self.markline]
            self.TKCanvas.itemconfig(lp["label"], font=self.font1)
            self.TKCanvas.itemconfig(lp["line"], width=self.width1)
            self.markline = -1
        return

    def _coloring_arrows(self, pindex):
        color = self.pointfigs[pindex][3]
        self.TKCanvas.itemconfig(self.arrow_l, activefill=color)
        self.TKCanvas.itemconfig(self.arrow_r, activefill=color)
        return

    def handler(self, event, values):
        if not self.proper:
            return

        clickx = values[event][0]
        clicky = int(values[event][1])
        figs = self.get_figures_at_location(values[event])
        nullisec = set(figs).isdisjoint(self.infofigs)
        unmarked = self.markline
        self._clearinfo()
        if not nullisec:
            return

        lfig = [lp["label"] for lp in self.linefigs]
        isec = set(figs).intersection(lfig)
        if len(isec) > 0:
            elem = lfig.index(list(isec)[0])
            if elem != unmarked:
                lp = self.linefigs[elem]
                self.TKCanvas.itemconfig(lp["label"], font=self.font1 + " bold")
                self.TKCanvas.itemconfig(lp["line"], width=self.width2)
                for fig in range(lp["label"]+1, lp["line"]+1):      # points + line
                    self.bring_figure_to_front(fig)
                self.markline = elem
            return

        p = -1
        if self.arrow_l in figs:
            p = self.point_index - 1 if self.point_index > 0 else len(self.pointfigs) - 1
        elif self.arrow_r in figs:
            p = self.point_index + 1 if self.point_index < len(self.pointfigs) - 1 else 0
        else:
            points = [pf[0] for pf in self.pointfigs]
            for f in figs:
                if f in points:
                    p = points.index(f)
                    break

        if p >= 0:
            self.point_index = p
            box = self.get_bounding_box(self.pointfigs[p][0])
            px = (box[0][0] + box[1][0]) / 2
            py = (box[0][1] + box[1][1]) / 2
            self._addinfo(self.draw_circle((px, py), self.circler, line_width=self.circlew,
                                           line_color=self.pointfigs[p][3],
                                           fill_color=self.canvascolor))

            self._coloring_arrows(p)

            if p == 0 or self.pointfigs[p][4] != self.pointfigs[p-1][4]:
                prev = 0
            else:
                prev = self.pointfigs[p][1] - self.pointfigs[p-1][1]
            y = self.canvash - self.MARGIN - 5
            textwidth = max(self.datewidth, self.valuewidth)
            if px > (self.chartx2 - self.chartx1) / 2:
                x1 = self.chartx1
                x2 = x1 + textwidth + 10
            else:
                x2 = self.chartx2
                x1 = x2 - textwidth - 10
            rows = 2
            txt = []
            txt.append("{}".format(self.pointfigs[p][2]))
            if prev != 0:
                txt.append("{:+,}".format(int(prev)))
                rows = 3
            txt.append("{:,}".format(int(self.pointfigs[p][1])))
            self._addinfo(self.draw_rectangle((x1, y - (self.text1h + 5) * rows),
                                              (x2, y + 5),
                                              line_color="black", fill_color="white"))
            for t in txt:
                self._addinfo(self.draw_text(t, (x2 - 5, y), font=self.font1,
                               text_location=sg.TEXT_LOCATION_TOP_RIGHT))
                y -= self.text1h + 5
        else:
            width = self.chartx2 - self.chartx1
            if self.chartx1 <= clickx <= self.chartx2 and \
               self.bottomtop <= clicky <= self.canvash - self.bottomtop:
                xrate = (clickx - self.chartx1) / width
                drate = round(self.wholeperiod * xrate, 0)
                dt = self.dt1 + datetime.timedelta(days=drate)
                y1 = max(self.MARGIN, int(self.text1h))
                y2 = self.canvash - y1
                self._addinfo(self.draw_line((clickx, y1), (clickx, y2), color=self.textcolor))
                tloc = self._info_location(clickx, self.datewidth)
                self._addinfo(self.draw_text(dt.strftime("%Y.%m.%d"),
                                             (clickx, self.canvash), font=self.font1,
                                             color=self.textcolor, text_location=tloc))
                value = (clicky - self.axis) * self.tolerance
                info1 = "{:,}".format(int(round(value, 0)))
                info2 = "± {:,}".format(int(self.tolerance))
                h = 2 * self.text1h + 12
                y = clicky - 5 if clicky > self.canvash / 2 else clicky + 5 + h
                tloc = self._info_location(clickx, self.valuewidth)
                self._addinfo(self.draw_text(info1, (clickx, y - 5), font=self.font1,
                                             color=self.canvascolor, text_location=tloc))
                self._addinfo(self.draw_text(info2, (clickx, y - 10 - self.text1h), font=self.font1,
                                             color=self.canvascolor, text_location=tloc))
                box11, box12 = self.get_bounding_box(self.infofigs[-2])
                box21, box22 = self.get_bounding_box(self.infofigs[-1])
                self._addinfo(self.draw_rectangle((min(box11[0], box21[0]) - 5, y),
                                                  (max(box12[0], box22[0]) + 5, y - h),
                                                  line_color=self.canvascolor,
                                                  fill_color=self.textcolor))
                self.bring_figure_to_front(self.infofigs[-3])
                self.bring_figure_to_front(self.infofigs[-2])
                self._addinfo(self.draw_point(values[event], size=5, color=self.textcolor))


SMALL_SIGN = "─"

class PieChart(sg.Graph):

    def _statistics(self, data):
        total = sum(data)
        count = len(data)
        avg = total / count
        stat = ["≡X{:,}".format(count),
                "ΣX{:,}".format(int(round(total, 0))),
                "ØX{:,}".format(int(round(avg, 0)))]
        return stat

    def activate(self, title, labels, data, **kwargs):
        canvasinit(self)
        if len(labels) == 0 or len(data) == 0 or len(labels) != len(data):
            self.proper = False
            return
        self.proper = True
        self.MARGIN = kwargs["margin"] if "margin" in kwargs else 10
        self.donut = kwargs["donut"] if "donut" in kwargs else True
        if isinstance(self.font2, str):
            font2size = int(self.font2.split(" ")[1])
        else:
            font2size = int(self.font2[1])
        self.linespace2 = int(round(font2size / 8, 0))
        self.LWIDTH = 2
        self.last_index = self.last_box = self.exploded = -1
        self.center_hole = self.center_text = self.messfig = -1
        self.messlen = 0
        self.pieparam = []
        color = ("red", "yellow", "green", "grey", "blue", "orange", "dark red",
                 "turquoise3", "gold2", "magenta2", "lime green", "purple1")

        # calibrating sizes
        labellen = max([len(_) for _ in labels])
        textw, text1h = figsize(self.font1, "X" * labellen)

        total = sum(data)
        stat = self._statistics(data)
        statw, self.text2h = figsize(self.font2, max(stat, key=len))

        self.erase()

        datafix = [dt if dt * self.canvash * math.pi / total > 1 else 0 for dt in data]
        totalfix = sum(datafix)
        startangle = 90
        c = 0
        for i, dt in enumerate(datafix):
            if dt == 0:
                self.pieparam.append({"label": labels[i], "value": data[i], "percent": data[i] / total,
                                      "start": startangle, "extent": 0, "color": "black",
                                      "rectfig": 0, "textfig": 0, "arcfig": -1})
            else:
                if dt == totalfix:
                    extangle = -359.99          # avoiding tkinter draw_arc bug
                else:
                    extangle = -(dt * 360 / totalfix)
                self.pieparam.append({"label": labels[i], "value": data[i], "percent": data[i] / total,
                                      "start": startangle, "extent": extangle, "color": color[c],
                                      "rectfig": 0, "textfig": 0, "arcfig": 0})
                startangle += extangle
                c = 0 if c == len(color) - 1 else c + 1

        # drawing title
        if title == "":
            self.chartx1 = self.MARGIN
        else:
            temp = self.draw_text(title, (0, self.MARGIN),
                                  font=self.font2, color=self.textcolor, angle=90,
                                  text_location=sg.TEXT_LOCATION_TOP_LEFT)
            self.chartx1 = self.get_bounding_box(temp)[1][0] + self.MARGIN
        self.chartx2 = self.chartx1 + self.canvash - self.MARGIN * 2
        self.explplus = min((self.canvash - self.MARGIN * 2) / 20, self.MARGIN)

        # drawing labels
        self.labelscale = text1h / 20
        labelx = self.canvasw - self.MARGIN - textw
        labely = self.MARGIN + text1h
        for pp in reversed(self.pieparam):
            txt = pp["label"].ljust(labellen * 2)
            pp["rectfig"] = self.draw_rectangle((labelx-25,labely), (labelx-5,labely-text1h),
                                                fill_color=pp["color"])
            if pp["arcfig"] < 0:
                self.draw_text(SMALL_SIGN, (labelx-15, labely-text1h/2), color="white", font=self.font1,
                               text_location=sg.TEXT_LOCATION_CENTER)
            pp["textfig"] = self.draw_text(txt, (labelx,labely),
                                           font=self.font1, color=self.textcolor,
                                           text_location=sg.TEXT_LOCATION_TOP_LEFT)
            self.draw_line((labelx, labely+1), (self.canvasw - self.MARGIN, labely+1),
                           color=self.linecolor)
            labely += text1h + 2
        self.draw_line((labelx, self.MARGIN-1), (self.canvasw - self.MARGIN, self.MARGIN-1),
                       color=self.linecolor)

        # drawing arcs
        for pp in self.pieparam:
            if pp["arcfig"] == 0:
                pp["arcfig"] = self.draw_arc((self.chartx1, self.canvash - self.MARGIN),
                                    (self.chartx2, self.MARGIN),
                                    start_angle=pp["start"], extent=pp["extent"],
                                    fill_color=pp["color"], arc_color=self.canvascolor,
                                    line_width=self.LWIDTH)
        self.figlist = []
        self.figlist.extend([pp["rectfig"] for pp in self.pieparam])
        self.figlist.extend([pp["textfig"] for pp in self.pieparam])
        self.figlist.extend([pp["arcfig"] for pp in self.pieparam])
        if self.donut:
            x = (self.chartx1 + self.chartx2) / 2
            y = self.canvash / 2
            self.center_hole = self.draw_circle((x, y),
                                    (self.canvash - self.MARGIN * 2) / 4,
                                    fill_color=self.canvascolor,
                                    line_color=self.canvascolor, line_width=self.LWIDTH)
            self.center_text = self.draw_text("", (x, y), font=self.font2,
                                    text_location=sg.TEXT_LOCATION_CENTER)

        # drawing statistics
        labelx -= 25
        self.info_fit = (statw < labelx - self.chartx2)
        if self.info_fit:
            x1 = self.chartx2 + (labelx - self.chartx2 - statw) / 2
            x2 = labelx - (labelx - self.chartx2 - statw) / 2
            h = len(stat) * (self.text2h + self.linespace2) - self.linespace2
            y = self.canvash - (self.canvash - h) / 2
            statfig = []
            for i in range(len(stat)):
                txt = stat[i]
                textfig1 = self.draw_text(txt[0], (x1,y), font=self.font2, color=self.linecolor,
                               text_location=sg.TEXT_LOCATION_TOP_LEFT)
                textfig2 = self.draw_text(txt[2:], (x2,y), font=self.font2, color=self.textcolor,
                               text_location=sg.TEXT_LOCATION_TOP_RIGHT)
                y -= (self.text2h + self.linespace2)
                statfig.append([textfig1, textfig2])
            self.statbb1 = self.get_bounding_box(statfig[0][0])
            self.statbb2 = self.get_bounding_box(statfig[1][1])
            self.info_center = self.chartx2 + (labelx - self.chartx2) / 2
        return

    def _clicked_item(self, loc):
        k = -1
        if loc[0] <= self.canvasw - self.MARGIN:
            figs = self.get_figures_at_location(loc)
            if len(figs) > 0 and self.center_hole not in figs and self.center_text not in figs:
                if figs[0] == self.exploded:
                    k = self.last_index
                elif figs[0] in self.figlist:
                    k = self.figlist.index(figs[0]) % len(self.pieparam)
        return k

    def _unselect(self):
        if self.exploded >= 0:
            self.delete_figure(self.exploded)
        if self.last_box >= 0:
            self.delete_figure(self.last_box)
        if self.center_text >= 0:
            self.delete_figure(self.center_text)
        if not self.donut:
            self.delete_figure(self.center_hole)
            self.center_hole = -1
        if self.messfig >= 0:
            for i in range(self.messlen):
                self.delete_figure(self.messfig - i)
        self.exploded = self.last_box = self.center_text = self.messfig = -1
        return

    def _label_box(self, textfig):
        lbox, rbox = self.get_bounding_box(textfig)
        rbox = (self.canvasw - self.MARGIN, rbox[1])
        box_figid = self.draw_rectangle(lbox, rbox)
        return box_figid

    def _item_message(self, msgtext, color, no_arc=False):
        if self.info_fit:
            bb11, bb12 = self.statbb1
            bb21, bb22 = self.statbb2
            x = (bb11[0] + bb12[0]) / 2
            w = abs(bb11[1] - bb12[1]) / self.labelscale
            self.draw_rectangle((x-w/2, bb11[1]), (x+w/2, bb12[1]), fill_color=color)
            if no_arc:
                self.draw_text(SMALL_SIGN, (x, (bb11[1]+bb12[1]) / 2), color="white", font=self.font2,
                               text_location=sg.TEXT_LOCATION_CENTER)
                self.messlen = 4
            else:
                self.messlen = 3
            self.draw_rectangle((bb21[0], bb11[1]), (bb22[0], bb12[1]),
                                line_color=self.linecolor, fill_color=self.linecolor)
            self.messfig = self.draw_text(msgtext, (bb22[0]-1, bb12[1]),
                                          font=self.font2, color=self.textcolor,
                                          text_location=sg.TEXT_LOCATION_BOTTOM_RIGHT)
        return

    def handler(self, event, values):
        if not self.proper:
            return None

        k = self._clicked_item(values[event])
        if k < 0:
            return None
        ppitem = self.pieparam[k]
        self._unselect()
        if k == self.last_index:
            self.last_index = -1
            return -k

        self.last_index = k
        self.last_box = self._label_box(ppitem["textfig"])
        self._item_message("{:,}".format(ppitem["value"]), ppitem["color"], ppitem["arcfig"] < 0)
        if ppitem["arcfig"] < 0:
            r = (self.canvash - self.MARGIN * 2) / 2 + self.explplus
            angle = math.radians(ppitem["start"])
            x1 = (self.chartx1 + self.chartx2) / 2
            y1 = self.canvash / 2
            x2 = x1 + r * math.cos(angle)
            y2 = y1 + r * math.sin(angle)
            self.exploded = self.draw_line((x1, y1), (x2, y2), width=self.LWIDTH)
        else:
            x1 = self.chartx1 - self.explplus
            y1 = self.canvash - self.MARGIN + self.explplus
            x2 = self.chartx2 + self.explplus
            y2 = self.MARGIN - self.explplus
            self.exploded = self.draw_arc((x1, y1), (x2, y2),
                                start_angle=ppitem["start"], extent=ppitem["extent"],
                                fill_color=ppitem["color"], arc_color=self.canvascolor,
                                line_width=self.LWIDTH)
        self.center_text = self.draw_text("{:.2%}".format(ppitem["percent"]),
                                ((self.chartx1 + self.chartx2) / 2, self.canvash / 2),
                                color=self.textcolor if self.donut else "white",
                                font=self.font2, text_location=sg.TEXT_LOCATION_CENTER)
        if not self.donut:
            box1, box2 = self.get_bounding_box(self.center_text)
            self.center_hole = self.draw_rectangle(box1, box2, fill_color="black")
        self.bring_figure_to_front(self.center_hole)
        self.bring_figure_to_front(self.center_text)

        return k


if __name__ == "__main__":
    pass
