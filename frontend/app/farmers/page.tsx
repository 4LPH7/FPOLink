"use client";

import React, { useState, useEffect } from "react";
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
import {
  Search,
  UserPlus,
  ShieldCheck,
  ShieldAlert,
  RefreshCw,
  Phone,
  CheckCircle2,
  Clock,
} from "lucide-react";
import { getFPOs, getFarmers, Farmer, FPO } from "@/lib/api";

export default function FarmersPage() {
  const { lang } = useLanguage();
  const [farmers, setFarmers] = useState<Farmer[]>([]);
  const [fpos, setFpos] = useState<FPO[]>([]);
  const [activeFpo, setActiveFpo] = useState<FPO | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [consentFilter, setConsentFilter] = useState<"all" | "granted" | "pending">("all");
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadData = async () => {
    setIsRefreshing(true);
    try {
      const fpoList = await getFPOs();
      setFpos(fpoList);
      const primaryFpo = fpoList[0] || null;
      setActiveFpo(primaryFpo);

      if (primaryFpo) {
        const res = await getFarmers(primaryFpo.id, undefined, searchTerm);
        setFarmers(res.farmers);
      }
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSearch = async (term: string) => {
    setSearchTerm(term);
    if (activeFpo) {
      const res = await getFarmers(activeFpo.id, undefined, term);
      setFarmers(res.farmers);
    }
  };

  const filteredFarmers = farmers.filter((f) => {
    if (consentFilter === "granted") return Boolean(f.notice_sent_at || f.alerts_opt_in);
    if (consentFilter === "pending") return !f.notice_sent_at && !f.alerts_opt_in;
    return true;
  });

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
          <Button
            variant="outline"
            size="sm"
            className="h-8"
            onClick={loadData}
            disabled={isRefreshing}
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1 text-muted-foreground ${isRefreshing ? "animate-spin" : ""}`} />
            {lang === "ta" ? "புதுப்பி" : "Refresh"}
          </Button>
          <Button size="sm" className="h-8">
            <UserPlus className="w-3.5 h-3.5 mr-1.5" />
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
                    ? "பெயர், கிராமம் அல்லது வட்டம் மூலம் தேடுக..."
                    : "Search by farmer name, village, or taluk..."
                }
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-9 h-10"
              />
            </div>
            <div className="flex items-center space-x-2 w-full sm:w-auto">
              <Badge
                variant={consentFilter === "all" ? "default" : "outline"}
                className="h-8 px-3 py-1 cursor-pointer"
                onClick={() => setConsentFilter("all")}
              >
                {lang === "ta" ? "அனைத்து விவசாயிகள்" : "All Farmers"}
              </Badge>
              <Badge
                variant={consentFilter === "granted" ? "default" : "outline"}
                className="h-8 px-3 py-1 cursor-pointer"
                onClick={() => setConsentFilter("granted")}
              >
                {lang === "ta" ? "ஒப்புதல் பெற்றவை" : "Consent Active"}
              </Badge>
              <Badge
                variant={consentFilter === "pending" ? "default" : "outline"}
                className="h-8 px-3 py-1 cursor-pointer"
                onClick={() => setConsentFilter("pending")}
              >
                {lang === "ta" ? "நிலுவையில்" : "Pending"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Farmer Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">
                {lang === "ta" ? "பதிவு செய்யப்பட்ட விவசாயிகள்" : "Registered Member Farmers"}
              </CardTitle>
              <CardDescription>
                {lang === "ta"
                  ? "DPDP சட்டம் பிரிவு 8-ன் படி வாட்ஸ்அப் முதல்-தொடர்பு அறிவிப்பு காலம் மற்றும் ஒப்புதல் தணிக்கை."
                  : "DPDP Section 8 compliance: First-contact notice timestamp & WhatsApp consent tracking."}
              </CardDescription>
            </div>
            <Badge variant="secondary">
              {filteredFarmers.length} {lang === "ta" ? "உழவர்கள்" : "Farmers"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{lang === "ta" ? "பெயர்" : "Name"}</TableHead>
                <TableHead>{lang === "ta" ? "கிராமம் / வட்டம்" : "Village / Taluk"}</TableHead>
                <TableHead>{lang === "ta" ? "நிலப்பரப்பு" : "Land Area"}</TableHead>
                <TableHead>{lang === "ta" ? "தொலைபேசி" : "Phone"}</TableHead>
                <TableHead>{lang === "ta" ? "DPDP ஒப்புதல் நிலை" : "DPDP Status"}</TableHead>
                <TableHead>{lang === "ta" ? "விலை அறிவிப்புகள்" : "Price Alerts"}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground text-sm">
                    {lang === "ta" ? "விவசாயிகள் பட்டியல் ஏற்றப்படுகிறது..." : "Loading farmer records..."}
                  </TableCell>
                </TableRow>
              ) : filteredFarmers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground text-sm">
                    {lang === "ta"
                      ? "தேடலுக்குரிய விவசாயிகள் எவரும் இல்லை."
                      : "No farmers match the current search or filter."}
                  </TableCell>
                </TableRow>
              ) : (
                filteredFarmers.map((f) => {
                  const hasConsent = Boolean(f.notice_sent_at || f.alerts_opt_in);
                  const maskedPhone = f.phone
                    ? f.phone.replace(/(\+?\d{2,5}\s?\d{3})\d{4}/, "$1••••")
                    : "—";

                  return (
                    <TableRow key={f.id}>
                      <TableCell className="font-semibold text-foreground">
                        {f.name}
                      </TableCell>
                      <TableCell>
                        {f.village}, {f.taluk}
                      </TableCell>
                      <TableCell>
                        {f.farm_area_acres} {lang === "ta" ? "ஏக்கர்" : "acres"}
                      </TableCell>
                      <TableCell className="font-mono text-xs text-muted-foreground">
                        {maskedPhone}
                      </TableCell>
                      <TableCell>
                        {hasConsent ? (
                          <Badge variant="success" className="gap-1">
                            <ShieldCheck className="w-3 h-3" />
                            <span>{lang === "ta" ? "அறிவிப்பு வழங்கப்பட்டது" : "Notice Logged"}</span>
                          </Badge>
                        ) : (
                          <Badge variant="warning" className="gap-1">
                            <Clock className="w-3 h-3" />
                            <span>{lang === "ta" ? "நிலுவையில்" : "Pending First Notice"}</span>
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant={f.alerts_opt_in ? "default" : "secondary"}>
                          {f.alerts_opt_in
                            ? lang === "ta"
                              ? "இயக்கத்தில்"
                              : "Opted-In"
                            : lang === "ta"
                            ? "நிறுத்தப்பட்டது"
                            : "Off"}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
