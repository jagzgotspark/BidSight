"use client";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { TenderListResponse } from "@/types/tender";
import TenderCard from "./TenderCard";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState } from "react";

export default function TenderFeed() {
  const [search, setSearch] = useState("");
  const [source, setSource] = useState("all");
  const [category, setCategory] = useState("all");

  const { data, isLoading, isError } = useQuery<TenderListResponse>({
    queryKey: ["tenders", search, source, category],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (search) params.search = search;
      if (source !== "all") params.source = source;
      if (category !== "all") params.category = category;
      const res = await api.get("/tenders/", { params });
      return res.data;
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex gap-3 flex-wrap">
        <Input placeholder="Search tenders..." className="max-w-xs"
          value={search} onChange={(e) => setSearch(e.target.value)} />
        <Select value={source} onValueChange={setSource}>
          <SelectTrigger className="w-36"><SelectValue placeholder="Source" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All sources</SelectItem>
            <SelectItem value="gem">GeM</SelectItem>
            <SelectItem value="cppp">CPPP</SelectItem>
          </SelectContent>
        </Select>
        <Select value={category} onValueChange={setCategory}>
          <SelectTrigger className="w-44"><SelectValue placeholder="Category" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            <SelectItem value="it_software">IT / Software</SelectItem>
            <SelectItem value="cloud">Cloud</SelectItem>
            <SelectItem value="ai_ml">AI / ML</SelectItem>
            <SelectItem value="cybersecurity">Cybersecurity</SelectItem>
            <SelectItem value="consulting">Consulting</SelectItem>
            <SelectItem value="infrastructure">Infrastructure</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground py-12 text-center">Loading tenders...</p>}
      {isError && <p className="text-sm text-destructive py-12 text-center">Could not connect to API. Make sure the backend is running.</p>}
      {data && data.items.length === 0 && (
        <p className="text-sm text-muted-foreground py-12 text-center">No tenders yet. Run the scraper to populate data.</p>
      )}
      {data && data.items.map((tender) => <TenderCard key={tender.id} tender={tender} />)}
      {data && data.total > 0 && (
        <p className="text-xs text-muted-foreground text-right">Showing {data.items.length} of {data.total} tenders</p>
      )}
    </div>
  );
}