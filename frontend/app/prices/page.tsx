"use client";

import React from "react";
import { useLanguage } from "@/lib/i18n/context";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { TrendingUp, RefreshCw, BarChart2, ShieldAlert } from "lucide-react";

export default function PricesPage() {
  const { lang, t } = useLanguage();

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
            {lang === "ta" ? "மண்டி விலைகள் & முன்கணிப்பு நுண்ணறிவு" : "Market Prices & Forecast Telemetry"}
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            {lang === "ta"
              ? "ஈரோடு மாவட்ட சந்தை விலைகள், CEDA/OGD நேரலை வரத்து, மற்றும் அடுத்த மாத முன்கணிப்பு."
              : "Erode district mandi feeds, CEDA/OGD live arrivals, and ML price predictions."}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="success">
            {lang === "ta" ? "OGD/CEDA நேரலை" : "OGD/CEDA Live"}
          </Badge>
          <Button variant="outline" size="sm" className="h-8">
            <RefreshCw className="w-3.5 h-3.5 mr-1 text-muted-foreground" />
            {lang === "ta" ? "புதுப்பி" : "Refresh"}
          </Button>
        </div>
      </div>

      {/* Featured Price Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="border-l-4 border-l-amber-500">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                {lang === "ta" ? "மஞ்சள் (விரலி)" : "Turmeric (Finger)"}
              </span>
              <Badge variant="warning">
                {lang === "ta" ? "வைத்திருத்தல் பரிந்துரை" : "HOLD SIGNAL"}
              </Badge>
            </div>
            <CardTitle className="text-3xl font-extrabold text-foreground mt-1">
              ₹12,350 <span className="text-sm font-normal text-muted-foreground">/ {lang === "ta" ? "குவிண்டால்" : "quintal"}</span>
            </CardTitle>
            <CardDescription>
              {lang === "ta"
                ? "பெருந்துறை ஒழுங்குமுறை விற்பனைக்கூடம் • நேற்று ₹12,200 (+1.2%)"
                : "Perundurai Regulated Mandi • Prev: ₹12,200 (+1.2%)"}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0 text-xs text-muted-foreground">
            {lang === "ta"
              ? "அடுத்த மாத கணிப்பு: ₹12,800/குவிண்டால் (நம்பகத்தன்மை: 85%)"
              : "Next month forecast: ₹12,800/quintal (Confidence: 85%)"}
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-500">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                {lang === "ta" ? "வாழை (நேந்திரன்)" : "Banana (Nendran)"}
              </span>
              <Badge variant="success">
                {lang === "ta" ? "சந்தையில் விற்றல்" : "SELL SIGNAL"}
              </Badge>
            </div>
            <CardTitle className="text-3xl font-extrabold text-foreground mt-1">
              ₹38 <span className="text-sm font-normal text-muted-foreground">/ {lang === "ta" ? "கிலோ" : "kg"}</span>
            </CardTitle>
            <CardDescription>
              {lang === "ta"
                ? "கோபிசெட்டிபாளையம் சந்தை • நேற்று ₹37 (+2.7%)"
                : "Gobichettipalayam Mandi • Prev: ₹37 (+2.7%)"}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0 text-xs text-muted-foreground">
            {lang === "ta"
              ? "வரத்து உச்ச நிலை — அடுத்த 7 நாட்களில் விலை குறைய வாய்ப்பு."
              : "Peak arrivals detected — potential price softening over next 7 days."}
          </CardContent>
        </Card>
      </div>

      {/* Wireframe Mandi Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            {lang === "ta" ? "ஈரோடு மாவட்ட மண்டி விலைகள் பட்டியல்" : "Erode District Mandi Price Feed"}
          </CardTitle>
          <CardDescription>
            {lang === "ta"
              ? "நேரலை மண்டி விலைகள், முரண்பாடு நிலை மற்றும் மாதிரி விலை விவரங்கள்."
              : "Live verified price records from official agricultural market committees."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{lang === "ta" ? "பயிர்" : "Crop"}</TableHead>
                <TableHead>{lang === "ta" ? "மண்டி" : "Mandi"}</TableHead>
                <TableHead>{lang === "ta" ? "மாதிரி விலை" : "Modal Price"}</TableHead>
                <TableHead>{lang === "ta" ? "வரம்பு (குறைவு - உயர்வு)" : "Range (Min - Max)"}</TableHead>
                <TableHead>{lang === "ta" ? "ஆதாரம்" : "Source"}</TableHead>
                <TableHead>{lang === "ta" ? "நிலை" : "Status"}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-semibold">{lang === "ta" ? "மஞ்சள்" : "Turmeric"}</TableCell>
                <TableCell>{lang === "ta" ? "பெருந்துறை" : "Perundurai"}</TableCell>
                <TableCell className="font-bold text-emerald-700">₹12,350 / q</TableCell>
                <TableCell>₹11,650 - ₹12,850</TableCell>
                <TableCell><Badge variant="outline">OGD Live</Badge></TableCell>
                <TableCell><Badge variant="success">{lang === "ta" ? "சரிபார்க்கப்பட்டது" : "Verified"}</Badge></TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-semibold">{lang === "ta" ? "வாழை" : "Banana"}</TableCell>
                <TableCell>{lang === "ta" ? "கோபிசெட்டிபாளையம்" : "Gobi"}</TableCell>
                <TableCell className="font-bold text-emerald-700">₹3,800 / q</TableCell>
                <TableCell>₹3,400 - ₹4,100</TableCell>
                <TableCell><Badge variant="outline">CEDA Mandi</Badge></TableCell>
                <TableCell><Badge variant="success">{lang === "ta" ? "சரிபார்க்கப்பட்டது" : "Verified"}</Badge></TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-semibold">{lang === "ta" ? "தேங்காய்" : "Coconut"}</TableCell>
                <TableCell>{lang === "ta" ? "செம்மாம்பாளையம்" : "Semmampalayam"}</TableCell>
                <TableCell className="font-bold text-emerald-700">₹2,800 / 100 pcs</TableCell>
                <TableCell>₹2,600 - ₹3,050</TableCell>
                <TableCell><Badge variant="outline">OGD Live</Badge></TableCell>
                <TableCell><Badge variant="success">{lang === "ta" ? "சரிபார்க்கப்பட்டது" : "Verified"}</Badge></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
