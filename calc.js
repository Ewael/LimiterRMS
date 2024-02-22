var co = new Object();
function recalc_onclick(ctl) {
  if (true) {
    co["xlew_3_3_2"] = eegetdropdownvalue(
      document.formc.elements["xlew_3_3_2"]
    );
    co["xlew_3_4_2"] = eegetdropdownvalue(
      document.formc.elements["xlew_3_4_2"]
    );
    co["hp"] = eeparseFloat(document.getElementById("hp").value);
    co["impedance"] = eeparseFloat(document.getElementById("impedance").value);
    co["ampli"] = eeparseFloat(document.getElementById("ampli").value);
    co["gain"] = eeparseFloat(document.getElementById("gain").value);
    calc(co);
    document.getElementById("xlew_3_11_2").value = eedisplayFloat(
      co["xlew_3_11_2"]
    );
    document.getElementById("xlew_3_11_3").value = co["xlew_3_11_3"];
  }
}
function calc(data) {
  var ampli_gain = data["gain"];
  var ampli_power = data["ampli"];
  var impedance = data["impedance"];
  var HP_power = data["hp"];
  var baffle_type = data["xlew_3_4_2"];
  var limiter_type = data["xlew_3_3_2"];
  var unit = str_eq(limiter_type, "dBu") ? " dBu" : " dB";
  var lim_hp_open = 20 * log10(Math.sqrt((HP_power / 1.5625) * impedance) / 0.775) - ampli_gain;
  var lim_hp_sealed = 20 * log10(Math.sqrt((HP_power / 2.34375) * impedance) / 0.775) - ampli_gain;
  var lim_ampli = 20 * log10(Math.sqrt((ampli_power / 2) * impedance) / 0.775) - ampli_gain;
  var lim_hp = str_eq(baffle_type, "ouverte") ? lim_hp_open : lim_hp_sealed;
  var truc_open = 20 * log10(Math.sqrt((HP_power / 1.5625) * impedance) / 0.775) - ampli_gain - 22;
  var truc_sealed =
    20 * log10(Math.sqrt((HP_power / 2.34375) * impedance) / 0.775) - ampli_gain - 22;
  var c6B14 = str_eq(baffle_type, "ouverte") ? truc_open + 1.5 : truc_sealed + 1.5;
  var c6B15 = str_eq(baffle_type, "ouverte") ? truc_open + 3.75 : truc_sealed + 3.75;
  var c6B18 =
    20 * log10(Math.sqrt((ampli_power / 2) * impedance) / 0.775) - ampli_gain - 22 + 1.5;
  var c6B19 =
    20 * log10(Math.sqrt((ampli_power / 2) * impedance) / 0.775) - ampli_gain - 22 + 3.75;
  var lim_dbu = lim_ampli > lim_hp ? lim_hp : lim_ampli;
  var c6B21 = c6B18 > c6B14 ? c6B14 : c6B18;
  var c6B22 = c6B19 > c6B15 ? c6B15 : c6B19;
  var c6B1 = lim_dbu - 2.5;
  var lim = lim_dbu > 0 ? rounddown(lim_dbu, 1) : roundup(lim_dbu, 1);
  var res_t.racks = c6B1 > 0 ? rounddown(lim_dbu - 2.5, 0) : roundup(lim_dbu - 2.5, 0);
  var res_DCX2496_sub = c6B21 > 0 ? rounddown(c6B21, 1) : roundup(c6B21, 1);
  var res_DCX2496_top = c6B22 > 0 ? rounddown(c6B22, 1) : roundup(c6B22, 1);
  var res = str_eq(limiter_type, "dBu")
    ? lim
    : str_eq(limiter_type, "T.Racks DS2/4")
    ? res_t.racks
    : str_eq(limiter_type, "DCX2496 SUB")
    ? res_DCX2496_sub
    : str_eq(limiter_type, "DCX2496 Top")
    ? res_DCX2496_top
    : 0;
  data["xlew_3_11_3"] = unit;
  data["xlew_3_11_2"] = res;
}
function postcode() {}
function TriggerOnchange(hiddenId) {
  var e = jQuery.Event("change");
  $("#" + hiddenId).trigger(e);
}
var eeisus = 0;
var eetrue = "TRUE";
var eefalse = "FALSE";
var eedec = ".";
var eeth = " ";
var eedecreg = new RegExp("\\.", "g");
var eethreg = new RegExp(" ", "g");
var eecurrencyreg = new RegExp("€", "g");
var eepercentreg = new RegExp("%", "g");
var fmtdaynamesshort = new Array(
  "dim.",
  "lun.",
  "mar.",
  "mer.",
  "jeu.",
  "ven.",
  "sam."
);
var fmtdaynameslong = new Array(
  "dimanche",
  "lundi",
  "mardi",
  "mercredi",
  "jeudi",
  "vendredi",
  "samedi"
);
var fmtmonthnamesshort = new Array(
  "janv.",
  "févr.",
  "mars",
  "avr.",
  "mai",
  "juin",
  "juil.",
  "août",
  "sept.",
  "oct.",
  "nov.",
  "déc."
);
var fmtmonthnameslong = new Array(
  "janvier",
  "février",
  "mars",
  "avril",
  "mai",
  "juin",
  "juillet",
  "août",
  "septembre",
  "octobre",
  "novembre",
  "décembre"
);
var fmtstrings = new Array(":");
var fmtdate1 = [12, 32, 17];
function str_eq(x, y) {
  if (isNaN(x) && isNaN(y)) return x.toLowerCase() == y.toLowerCase();
  else return x == y;
}

function eegetdropdownvalue(ctl) {
  var control = $(ctl);
  var tag = control.get(0).tagName;
  var val;
  if (tag == "INPUT") {
    val = $("input[name=" + control.attr("name") + "]:checked").attr(
      "data-value"
    );
  } else if (tag == "SELECT") {
    val = control
      .find(":selected")
      .attr(
        "data-value"
      ); /* data-value contains type and value, eg. n:100 (number), b:true (bool), s:ram (string) */
  } else {
    val = control.val();
  }
  return val == undefined ? 0 : eeunpackdropdownvalue(val);
}

function myIsNaN(x) {
  return isNaN(x) || (typeof x == "number" && !isFinite(x));
}

function log10(x) {
  return Math.log(x) / Math.LN10;
}

function mod(n, d) {
  return n - d * Math.floor(n / d);
}

function round(n, nd) {
  if (isFinite(n) && isFinite(nd)) {
    var sign_n = n < 0 ? -1 : 1;
    var abs_n = Math.abs(n);
    var factor = Math.pow(10, nd);
    return (sign_n * Math.round(abs_n * factor)) / factor;
  } else {
    return NaN;
  }
}

function rounddown(n, nd) {
  if (isFinite(n) && isFinite(nd)) {
    var sign_n = n < 0 ? -1 : 1;
    var abs_n = Math.abs(n);
    var factor = Math.pow(10, nd < 0 ? Math.ceil(nd) : Math.floor(nd));
    return (sign_n * Math.floor(abs_n * factor)) / factor;
  } else {
    return NaN;
  }
}

function roundup(n, nd) {
  if (isFinite(n) && isFinite(nd)) {
    var sign_n = n < 0 ? -1 : 1;
    var abs_n = Math.abs(n);
    var factor = Math.pow(10, nd < 0 ? Math.ceil(nd) : Math.floor(nd));
    return (sign_n * Math.ceil(abs_n * factor)) / factor;
  } else {
    return NaN;
  }
}

function eeparseFloat(str) {
  str = String(str).replace(eedecreg, ".");
  var res = parseFloat(str);
  if (isNaN(res)) {
    return 0;
  } else {
    return res;
  }
}

var near0RegExp = new RegExp("[.](.*0000000|.*9999999)");
function eedisplayFloat(x) {
  if (myIsNaN(x)) {
    return Number.NaN;
  } else {
    var str = String(x);
    if (near0RegExp.test(str)) {
      x = round(x, 8);
      str = String(x);
    }
    return str.replace(/\./g, eedec);
  }
}

function eedisplayScientific(x, nd) {
  if (myIsNaN(x)) {
    return Number.NaN;
  } else {
    var str = String(x.toExponential(nd));
    return str.replace(/\./g, eedec);
  }
}

function eedisplayFloatND(x, nd) {
  if (myIsNaN(x)) {
    return Number.NaN;
  } else {
    var res = round(x, nd);
    if (nd > 0) {
      var str = String(res);
      if (str.indexOf("e") != -1) return str;
      if (str.indexOf("E") != -1) return str;
      var parts = str.split(".");
      if (parts.length < 2) {
        var decimals = "00000000000000".substring(0, nd);
        return parts[0].toString() + eedec + decimals;
      } else {
        var decimals = (parts[1].toString() + "00000000000000").substring(
          0,
          nd
        );
        return parts[0].toString() + eedec + decimals;
      }
    } else {
      return res;
    }
  }
}

function eedisplayPercent(x) {
  if (myIsNaN(x)) {
    return Number.NaN;
  } else {
    return eedisplayFloat(x * 100) + "%";
  }
}

function eedisplayPercentND(x, nd) {
  if (myIsNaN(x)) {
    return Number.NaN;
  } else {
    return eedisplayFloatND(x * 100, nd) + "%";
  }
}

function eedisplayFloatNDTh(x, nd) {
  if (myIsNaN(x)) {
    return Number.NaN;
  } else {
    var res = round(x, nd);
    if (nd > 0) {
      var str = String(res);
      if (str.indexOf("e") != -1) return str;
      if (str.indexOf("E") != -1) return str;
      var parts = str.split(".");
      var res2 = eeinsertThousand(parts[0].toString());
      if (parts.length < 2) {
        var decimals = "00000000000000".substring(0, nd);
        return res2 + eedec + decimals;
      } else {
        var decimals = (parts[1].toString() + "00000000000000").substring(
          0,
          nd
        );
        return res2 + eedec + decimals;
      }
    } else {
      return eeinsertThousand(res.toString());
    }
  }
}

function eedisplayPercentNDTh(x, nd) {
  if (myIsNaN(x)) {
    return Number.NaN;
  } else {
    return eedisplayFloatNDTh(x * 100, nd) + "%";
  }
}

function eeinsertThousand(whole) {
  if (whole == "" || whole.indexOf("e") >= 0) {
    return whole;
  } else {
    var minus_sign = "";
    if (whole.charAt(0) == "-") {
      minus_sign = "-";
      whole = whole.substring(1);
    }
    var res = "";
    var str_length = whole.length - 1;
    for (var ii = 0; ii <= str_length; ii++) {
      if (ii > 0 && ii % 3 == 0) {
        res = eeth + res;
      }
      res = whole.charAt(str_length - ii) + res;
    }
    return minus_sign + res;
  }
}

function eedatefmt(fmt, x) {
  if (!isFinite(x)) return Number.NaN;
  var padding = 0;
  var tmp = 0;
  var res = "";
  var len = fmt.length;
  for (var ii = 0; ii < len; ii++) {
    if (fmt[ii] > 31) {
      res += fmtstrings[fmt[ii] - 32];
    } else {
      switch (fmt[ii]) {
        case 2:
          res += eemonth(x);
          break;
        case 3:
          tmp = eemonth(x);
          if (tmp < 10) {
            res += "0";
          }
          res += tmp;
          break;
        case 4:
          res += fmtmonthnamesshort[eemonth(x) - 1];
          break;
        case 5:
          res += fmtmonthnameslong[eemonth(x) - 1];
          break;
        case 6:
          res += eeday(x);
          break;
        case 7:
          tmp = eeday(x);
          if (tmp < 10) {
            res += "0";
          }
          res += tmp;
          break;
        case 8:
          res += fmtdaynamesshort[weekday(x, 1) - 1];
          break;
        case 9:
          res += fmtdaynameslong[weekday(x, 1) - 1];
          break;
        case 10:
          tmp = year(x) % 100;
          if (tmp < 10) {
            res += "0";
          }
          res += tmp;
          break;
        case 11:
          res += year(x);
          break;
        case 12:
          res += hour(x);
          break;
        case 13:
          tmp = hour(x);
          if (tmp < 10) {
            res += "0";
          }
          res += tmp;
          break;
        case 14:
          tmp = hour(x) % 12;
          if (tmp == 0) {
            res += "12";
          } else {
            res += tmp % 12;
          }
          break;
        case 15:
          tmp = hour(x) % 12;
          if (tmp == 0) {
            res += "12";
          } else {
            if (tmp < 10) {
              res += "0";
            }
            res += tmp;
          }
          break;
        case 16:
          res += minute(x);
          break;
        case 17:
          tmp = minute(x);
          if (tmp < 10) {
            res += "0";
          }
          res += tmp;
          break;
        case 18:
          res += second(x);
          break;
        case 19:
          tmp = second(x);
          if (tmp < 10) {
            res += "0";
          }
          res += tmp;
          break;
        case 21:
        case 22:
          if (hour(x) < 12) {
            res += "AM";
          } else {
            res += "PM";
          }
          break;
        case 23:
          res += eedisplayFloat(x);
          break;
        case 24:
          tmp = fmt[++ii];
          res += eedisplayFloatND(x, tmp);
          break;
        case 25:
          tmp = fmt[++ii];
          res += eedisplayFloatNDTh(x, tmp);
          break;
        case 26:
          res += eedisplayPercent(x);
          break;
        case 27:
          tmp = fmt[++ii];
          res += eedisplayPercentND(x, tmp);
          break;
        case 28:
          tmp = fmt[++ii];
          res += eedisplayPercentNDTh(x, tmp);
          break;
        case 29:
          tmp = fmt[++ii];
          res += eedisplayScientific(x, tmp);
          break;
        case 30:
          padding = fmt[++ii];
          tmp = hour(x) + Math.floor(x) * 24;
          tmp = tmp.toString();
          if (tmp.length < padding) {
            res += "00000000000000".substring(0, padding - tmp.length);
          }
          res += tmp;
          break;
      }
    }
  }
  return res;
}

function eeunpackdropdownvalue(val) {
  if (val.length < 2) return val;
  var typ = val.substring(0, 2);
  var data = val.substring(2);
  if (typ == "b:") return data.toLowerCase() == "true";
  if (typ == "n:") return parseFloat(data);
  if (typ == "s:") return data;
  return val;
}

function leap_gregorian(year) {
  return year % 4 == 0 && !(year % 100 == 0 && year % 400 != 0);
}
var GREGORIAN_EPOCH = 1721425;
function gregorian_to_jd(year, month, day) {
  return (
    GREGORIAN_EPOCH -
    0 +
    365 * (year - 1) +
    Math.floor((year - 1) / 4) +
    -Math.floor((year - 1) / 100) +
    Math.floor((year - 1) / 400) +
    Math.floor(
      (367 * month - 362) / 12 +
        (month <= 2 ? 0 : leap_gregorian(year) ? -1 : -2) +
        day
    )
  );
}
function jd_to_gregorian(jd) {
  var wjd,
    depoch,
    quadricent,
    dqc,
    cent,
    dcent,
    quad,
    dquad,
    yindex,
    year,
    yearday,
    leapadj;
  wjd = Math.floor(jd);
  depoch = wjd - GREGORIAN_EPOCH - 1;
  quadricent = Math.floor(depoch / 146097);
  dqc = mod(depoch, 146097);
  cent = Math.floor(dqc / 36524);
  dcent = mod(dqc, 36524);
  quad = Math.floor(dcent / 1461);
  dquad = mod(dcent, 1461);
  yindex = Math.floor(dquad / 365);
  year = quadricent * 400 + cent * 100 + quad * 4 + yindex;
  if (!(cent == 4 || yindex == 4)) {
    year++;
  }
  yearday = wjd - gregorian_to_jd(year, 1, 1);
  leapadj =
    wjd < gregorian_to_jd(year, 3, 1) ? 0 : leap_gregorian(year) ? 1 : 2;
  var month = Math.floor(((yearday + leapadj) * 12 + 373) / 367);
  var day = wjd - gregorian_to_jd(year, month, 1) + 1;
  return new Array(year, month, day);
}

function eeday(serial_number) {
  if (!isFinite(serial_number)) return Number.NaN;
  if (serial_number < 1) {
    return 0;
  }
  if (serial_number > 60) serial_number--;
  var res = jd_to_gregorian(serial_number + 2415020);
  return res[2];
}

function hour(serial_number) {
  if (!isFinite(serial_number)) return Number.NaN;
  var res = Math.floor(
    (serial_number - Math.floor(serial_number)) * 86400 + 0.5
  );
  return Math.floor(res / 3600);
}

function minute(serial_number) {
  if (!isFinite(serial_number)) return Number.NaN;
  var res = Math.floor(
    (serial_number - Math.floor(serial_number)) * 86400 + 0.5
  );
  return Math.floor(res / 60) % 60;
}

function eemonth(serial_number) {
  if (!isFinite(serial_number)) return Number.NaN;
  if (serial_number < 1) {
    return 1;
  }
  if (serial_number > 60) serial_number--;
  var res = jd_to_gregorian(serial_number + 2415020);
  return res[1];
}

function second(serial_number) {
  if (!isFinite(serial_number)) return Number.NaN;
  var res = Math.floor(
    (serial_number - Math.floor(serial_number)) * 86400 + 0.5
  );
  return res % 60;
}

function weekday(serial_number, return_type) {
  if (!isFinite(return_type) || !isFinite(serial_number)) return Number.NaN;
  if (return_type < 1 || return_type > 3) return Number.NaN;
  var res = Math.floor(serial_number + 6) % 7;
  switch (Math.floor(return_type)) {
    case 1:
      return res + 1;
    case 2:
      return ((res + 6) % 7) + 1;
    case 3:
      return (res + 6) % 7;
  }
  return "hej";
}

function year(serial_number) {
  if (!isFinite(serial_number)) return Number.NaN;
  if (serial_number < 1) {
    return 1900;
  }
  if (serial_number > 60) serial_number--;
  var res = jd_to_gregorian(serial_number + 2415020);
  return res[0];
}
function eequerystring() {
  var variable, key, value, ii, querystring, variables;
  querystring = document.location.search;
  if (querystring.length > 0) {
    variables = querystring.substring(1).split("&");
    for (ii = 0; ii < variables.length; ii++) {
      variable = variables[ii].split("=");
      key = unescape(variable[0]);
      value = unescape(variable[1]);
      if (document.formc[key] != null) document.formc[key].value = value;
    }
  }
}
function LoadFromQueryString() {
  eequerystring();
}
function navigate(e) {
  var t = e.keyCode | e.which;
  if (t != 13 && t != 40 && t != 38) return;
  var n = $(e.target || e.srcElement);
  if (n.is("textarea")) return;
  if (n.is("select") && (t == 38 || t == 40)) return;
  var r = parseInt(n.attr("data-sheet"), 10);
  var i = parseInt(n.attr("data-row"), 10);
  var s = parseInt(n.attr("data-col"), 10);
  var o = false;
  var u = $("#sheet-" + r + "");
  var a =
    'input:not(":hidden,:button,[readonly=readonly],:disabled"),select,a.ui-slider-handle,textarea';
  var f = i + 1;
  var l = i - 1;
  var c = f;
  var h = l;
  while ((t == 40 && f <= c) || (t == 38 && l >= h)) {
    var p = u
      .find(a)
      .filter(
        "[data-sheet=" +
          r +
          "][data-row=" +
          (t == 38 ? l : f) +
          "][data-col=" +
          s +
          "]"
      );
    if (p.length > 0) {
      p.focus();
      if (p.is("input:text, textarea")) p.select();
      o = true;
      break;
    } else {
      var d;
      if (u.data("col" + s) == undefined) {
        d = u
          .find(a)
          .filter("[data-sheet=" + r + "][data-col=" + s + "]")
          .map(function () {
            return parseInt($(this).attr("data-row"), 10);
          })
          .toArray();
        u.data("col" + s, d);
      } else {
        d = u.data("col" + s);
      }
      c = d[d.length - 1];
      h = d[0];
      var v = "indexOf" in Array.prototype ? d.indexOf(i) : $.inArray(i, d);
      if (t == 40 && i < c) {
        f = d[v + 1];
      } else if (t == 38 && i > h) {
        l = d[v - 1];
      } else {
        break;
      }
    }
  }
  if (!o) {
    var m;
    if (t == 38) m = parseInt(n.attr("tabindex"), 10) - 1;
    else m = parseInt(n.attr("tabindex"), 10) + 1;
    var g = u
      .find(a)
      .filter("[data-sheet][data-row][data-col][tabindex=" + m + "]");
    if (g.length > 0) {
      if (g.is(":radio")) g = g.filter(":checked");
      if (g.length > 0) {
        g.focus();
        if (g.is("input:text, textarea")) g.select();
      }
    } else {
      var y = u
        .find(a)
        .filter("[data-sheet][data-row][data-col][tabindex]:first");
      y.focus();
      if (y.is("input:text, textarea")) y.select();
    }
  }
  e.preventDefault ? e.preventDefault() : (e.returnValue = false);
}
var _gaq = _gaq || [];
_gaq.push(["_setAccount", "UA-12493173-1"]);
_gaq.push(["_trackPageview"]);
(function () {
  var ga = document.createElement("script");
  ga.type = "text/javascript";
  ga.async = true;
  ga.src =
    ("https:" == document.location.protocol ? "https://ssl" : "http://www") +
    ".google-analytics.com/ga.js";
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(ga, s);
})();
var ssccf1n = function (op, id, css, data1) {
  switch (op) {
    case "image":
      $("#" + id).attr("src", $("#" + data1).attr("src"));
      break;
  }
};
var ssccf4n = function (op, id, colors, data1, data2, data3, data4) {
  switch (op) {
  }
};
