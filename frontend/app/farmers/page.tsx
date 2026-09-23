"use client";

import React, { useState } from "react";
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
import { Input } from "@/components/ui/input";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { Search, UserPlus, ShieldCheck, ShieldAlert, Phone } from "lucide-react";

export default function FarmersPage() {
  const { lang } = useLanguage();
  const [searchTerm, setSearchTerm] = useState("");

  const sampleFarmers = [
    {
      id: "1",
      nameTa: "முருகேசன் கே.",
      nameEn: "Murugesan K.",
      villageTa: "கொடுமுடி",
      villageEn: "Kodumudi",
      cropTa: "மஞ்சள் (3 ஏக்கர்)",
      cropEn: "Turmeric (3 Acres)",
      phone: "+91 98421 •••••",
      consent: true,
      alerts: true,
    },
    {
      id: "2",
      nameTa: "செந்தில்குமார் பி.",
      nameEn: "Senthilkumar P.",
      villageTa: "பெருந்துறை",
      villageEn: "Perundurai",
      cropTa: "வாழை (2 ஏக்கர்)",
      cropEn: "Banana (2 Acres)",
      phone: "+91 97892 •••••",
      consent: true,
      alerts: false,
    },
    {
      id: "3",
      nameTa: "பழனிச்சாமி ஆர்.",
      nameEn: "Palanisamy R.",
      villageTa: "மொடக்குறிச்சி",
      villageEn: "Modakkurichi",
      cropTa: "மஞ்சள் (5 ஏக்கர்)",
      cropEn: "Turmeric (5 Acres)",
      phone: "+91 94432 •••••",
      consent: false,
      alerts: false,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
            {lang === "ta" ? "உழவர் பதிவேடு & DPDP ஒப்புதல் நிலை" : "Farmer Directory & DPDP Consent Status"}
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            {lang === "ta"
              ? "FPO உறுப்பினர் விவசாயிகள், பயிர் பரப்பளவு, மற்றும் வாட்ஸ்அப் DPDP ஒப்புதல் பதிவுகள்."
              : "Registered FPO member farmers, farm holdings, and DPDP consent compliance status."}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button size="sm" className="h-9">
            <UserPlus className="w-4 h-4 mr-1.5" />
            {lang === "ta" ? "விவசாயி சேர்" : "Add Farmer"}
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="relative flex-1 w-full">
              <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
              <Input
                placeholder={
                  lang === "ta"
                    ? "பெயர் அல்லது கிராமம் மூலம் தேடுக..."
                    : "Search by farmer name or village..."
                }
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 h-10"
              />
            </div>
            <div className="flex items-center space-x-2 w-full sm:w-auto">
              <Badge variant="outline" className="h-8 px-3 py-1 cursor-pointer">
                {lang === "ta" ? "அனைத்து கிராமங்கள்" : "All Villages"}
              </Badge>
              <Badge variant="outline" className="h-8 px-3 py-1 cursor-pointer">
                {lang === "ta" ? "ஒப்புதல் பெற்றவை" : "Consent Active"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Farmer Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">
              {lang === "ta" ? "பதிவு செய்யப்பட்ட விவசாயிகள்" : "Registered Member Farmers"}
            </CardTitle>
            <Badge variant="secondary">3 {lang === "ta" ? "உழவர்கள்" : "Farmers"}</Badge>
          </div>
          <CardDescription>
            {lang === "ta"
              ? "DPDP சட்டத்தின் கீழ் விவசாயிகள் ஒப்புதல் நிலை முதன்மைப்படுத்தப்பட்டுள்ளது."
              : "DPDP Section 8 compliance: Consent audit logs tracked with timestamps."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{lang === "ta" ? "பெயர்" : "Name"}</TableHead>
                <TableHead>{lang === "ta" ? "கிராமம் / வட்டம்" : "Village / Taluk"}</TableHead>
                <TableHead>{lang === "ta" ? "முக்கிய பயிர்" : "Primary Crop"}</TableHead>
                <TableHead>{lang === "ta" ? "தொலைபேசி" : "Phone"}</TableHead>
                <TableHead>{lang === "ta" ? "DPDP ஒப்புதல்" : "DPDP Consent"}</TableHead>
                <TableHead>{lang === "ta" ? "விலை அறிவிப்புகள்" : "Price Alerts"}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sampleFarmers.map((f) => (
                <TableRow key={f.id}>
                  <TableCell className="font-semibold text-foreground">
                    {lang === "ta" ? f.nameTa : f.nameEn}
                  </TableCell>
                  <TableCell>{lang === "ta" ? f.villageTa : f.villageEn}</TableCell>
                  <TableCell>{lang === "ta" ? f.cropTa : f.cropEn}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {f.phone}
                  </TableCell>
                  <TableCell>
                    {f.consent ? (
                      <Badge variant="success" className="space-x-1">
                        <ShieldCheck className="w-3 h-3 mr-1" />
                        <span>{lang === "ta" ? "ஒப்புதல் உண்டு" : "Granted"}</span>
                      </Badge>
                    ) : (
                      <Badge variant="destructive" className="space-x-1">
                        <ShieldAlert className="w-3 h-3 mr-1" />
                        <span>{lang === "ta" ? "நிலுவையில்" : "Pending"}</span>
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={f.alerts ? "default" : "secondary"}>
                      {f.alerts
                        ? lang === "ta"
                          ? "இயக்கத்தில்"
                          : "Opted-In"
                        : lang === "ta"
                        ? "நிறுத்தப்பட்டது"
                        : "Off"}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
