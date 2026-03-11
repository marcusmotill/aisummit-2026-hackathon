import React, { useState, useEffect } from "react";
import { strategyClient, contentClient } from "./api";
import { 
  BarChart3, 
  Map, 
  PenTool, 
  Image as ImageIcon, 
  Loader2, 
  ArrowRight, 
  CheckCircle2,
  LayoutDashboard,
  Megaphone,
  Download
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

interface GapTopic {
  title: string;
  description: string;
  priority: string;
  estimated_impact: string;
}

interface GapReportData {
  summary: string;
  topics: GapTopic[];
}

interface CampaignAsset {
  title: string;
  content: string;
  visual_suggestion: string;
  channel: string;
}

interface CampaignReportData {
  summary: string;
  assets: CampaignAsset[];
}

// Minimal Markdown implementation if no lib is available
const SimpleMarkdown = ({ content }: { content: string }) => {
  return (
    <div className="prose dark:prose-invert max-w-none whitespace-pre-wrap font-mono text-sm">
      {content}
    </div>
  );
};

export default function Home() {
  const [activeTab, setActiveTab] = useState<"strategy" | "campaign">("strategy");
  const [strategyQuery, setStrategyQuery] = useState("Auditing patagonia.com to identify content gaps vs competitors like North Face in 2026.");
  const [strategySession, setStrategySession] = useState<string | null>(null);
  const [contentSession, setContentSession] = useState<string | null>(null);
  const [gapReport, setGapReport] = useState<GapReportData | null>(null);
  const [campaignReport, setCampaignReport] = useState<CampaignReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [artifacts, setArtifacts] = useState<string[]>([]);
  const [images, setImages] = useState<string[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<{
    strategy: boolean;
    content: boolean;
  }>({ strategy: true, content: true });

  const init = async () => {
    try {
      const isStrategyUp = await strategyClient.healthCheck();
      const isContentUp = await contentClient.healthCheck();
      
      setConnectionStatus({ strategy: isStrategyUp, content: isContentUp });

      if (isStrategyUp) {
        const sId = await strategyClient.createSession();
        setStrategySession(sId);
      }
      if (isContentUp) {
        const cId = await contentClient.createSession();
        setContentSession(cId);
      }
    } catch (err) {
      console.error("Failed to init sessions", err);
    }
  };

  // Initialize sessions
  useEffect(() => {
    init();
  }, []);

  const runStrategy = async () => {
    if (!strategySession) return;
    setLoading(true);
    try {
      await strategyClient.runAgent(strategySession, strategyQuery);
      // Poll for structured JSON artifact
      const artifact = await strategyClient.getArtifact(strategySession, "gap_report.json");
      if (artifact && artifact.text) {
        try {
          const data = JSON.parse(artifact.text) as GapReportData;
          setGapReport(data);
        } catch (e) {
          console.error("Failed to parse gap report JSON", e);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const runCampaign = async (topic: string) => {
    if (!contentSession) return;
    setLoading(true);
    setActiveTab("campaign");
    try {
      await contentClient.runAgent(contentSession, `Generate a full campaign for this topic: ${topic}`);
      
      await fetchCampaignArtifacts(contentSession);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCampaignArtifacts = async (sessionId: string) => {
    try {
      // Get structured JSON artifact
      const reportArtifact = await contentClient.getArtifact(sessionId, "campaign_report.json");
      if (reportArtifact && reportArtifact.text) {
        try {
          const data = JSON.parse(reportArtifact.text) as CampaignReportData;
          setCampaignReport(data);
        } catch (e) {
          console.error("Failed to parse campaign report JSON", e);
        }
      }

      // Check for images
      const allArtifacts = await contentClient.listArtifacts(sessionId);
      const imgArtifacts = allArtifacts.filter(a => a.startsWith("image_"));
      const imgData: string[] = [];
      for (const imgName of imgArtifacts) {
        const artifact = await contentClient.getArtifact(sessionId, imgName);
        if (artifact && artifact.inline_data) {
          const base64 = artifact.inline_data.data;
          const mime = artifact.inline_data.mime_type || "image/png";
          imgData.push(`data:${mime};base64,${base64}`);
        }
      }
      if (imgData.length > 0) {
        setImages(imgData);
      }
    } catch (err) {
      console.error("Failed to fetch campaign artifacts", err);
    }
  };

  // Auto-refresh artifacts when switching to campaign tab
  useEffect(() => {
    if (activeTab === "campaign" && contentSession) {
      fetchCampaignArtifacts(contentSession);
    }
  }, [activeTab, contentSession]);


  return (
    <div className="flex h-screen bg-zinc-50 dark:bg-zinc-950 transition-colors duration-300">
      {/* Sidebar */}
      <aside className="w-64 border-r border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 flex flex-col p-6 gap-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-500/30">
            <Megaphone size={22} strokeWidth={2.5} />
          </div>
          <h1 className="font-bold text-xl tracking-tight dark:text-white">ContentEngine</h1>
        </div>

        <nav className="flex flex-col gap-2">
          <button 
            onClick={() => setActiveTab("strategy")}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${activeTab === "strategy" ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300 font-semibold" : "text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"}`}
          >
            <BarChart3 size={20} />
            Strategy
          </button>
          <button 
            onClick={() => setActiveTab("campaign")}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${activeTab === "campaign" ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300 font-semibold" : "text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"}`}
          >
            <PenTool size={20} />
            Campaign
          </button>
        </nav>

        <div className="mt-auto p-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-xl border border-dashed border-zinc-200 dark:border-zinc-700">
          <p className="text-xs text-zinc-400 font-medium uppercase tracking-wider mb-2">System Status</p>
          <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400 font-medium">
            {connectionStatus.strategy && connectionStatus.content ? "Engines Active (2026)" : "Connection Issue Detected"}
          </div>
          {(!connectionStatus.strategy || !connectionStatus.content) && (
            <button 
              onClick={init}
              className="mt-2 w-full text-xs bg-indigo-600 text-white py-1.5 rounded-md font-bold hover:bg-indigo-700 transition"
            >
              Retry Connection
            </button>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8 lg:p-12">
        <AnimatePresence mode="wait">
          {activeTab === "strategy" ? (
            <motion.div 
              key="strategy"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="max-w-4xl mx-auto space-y-10"
            >
              <div className="space-y-4">
                <h2 className="text-4xl font-extrabold tracking-tight dark:text-white flex items-center gap-3">
                  <Map className="text-indigo-600" size={36} />
                  Opportunity Discovery
                </h2>
                <p className="text-lg text-zinc-500 max-w-2xl">
                  Analyze your brand authority and competitor trends to find high-impact content gaps.
                </p>
              </div>

              <div className="bg-white dark:bg-zinc-900 rounded-3xl p-8 shadow-xl shadow-zinc-200/50 dark:shadow-none border border-zinc-100 dark:border-zinc-800 space-y-6">
                <div className="relative group">
                  <textarea 
                    value={strategyQuery}
                    onChange={(e) => setStrategyQuery(e.target.value)}
                    className="w-full bg-zinc-50 dark:bg-zinc-800 border-none rounded-2xl p-6 h-32 focus:ring-2 focus:ring-indigo-500 transition-all text-lg placeholder:text-zinc-400 dark:text-white"
                    placeholder="Enter your strategy objective..."
                  />
                  <div className="absolute inset-0 rounded-2xl ring-1 ring-inset ring-zinc-900/5 dark:ring-white/10 pointer-events-none" />
                </div>
                
                <button 
                  onClick={runStrategy}
                  disabled={loading}
                  className="w-full h-14 bg-zinc-900 dark:bg-indigo-600 text-white rounded-2xl font-bold text-lg flex items-center justify-center gap-3 hover:scale-[1.01] active:scale-[0.99] transition-all disabled:opacity-50 disabled:hover:scale-100"
                >
                  {loading ? <Loader2 className="animate-spin" /> : <BarChart3 size={22} />}
                  {loading ? "Analyzing Marketplace..." : "Analyze Content Gaps"}
                </button>
              </div>

              {gapReport && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-6"
                >
                  <div className="flex items-center justify-between">
                    <h3 className="text-2xl font-bold dark:text-white">Strategic Gap Report</h3>
                    <div className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                       Active for 2026
                    </div>
                  </div>
                  
                  <div className="bg-white dark:bg-zinc-900 rounded-3xl p-8 shadow-lg border border-zinc-100 dark:border-zinc-800 space-y-8">
                    <div className="space-y-4">
                      <h4 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Executive Summary</h4>
                      <p className="text-lg text-zinc-700 dark:text-zinc-300 leading-relaxed font-medium">
                        {gapReport.summary}
                      </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {gapReport.topics.map((topic, i) => (
                        <div 
                          key={i}
                          className="group p-6 rounded-2xl bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-100 dark:border-zinc-700/50 hover:border-indigo-500 transition-all cursor-pointer relative overflow-hidden"
                          onClick={() => runCampaign(topic.title)}
                        >
                          <div className="absolute top-4 right-4 text-[10px] font-black uppercase px-2 py-0.5 rounded-md bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300">
                             Priority: {topic.priority}
                          </div>
                          <div className="space-y-3">
                            <h5 className="font-bold text-lg dark:text-white pr-16">{topic.title}</h5>
                            <p className="text-sm text-zinc-500 line-clamp-2">{topic.description}</p>
                            <div className="flex items-center justify-between pt-2">
                              <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-tighter">Impact: {topic.estimated_impact}</span>
                              <div className="p-2 bg-indigo-600 text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                                <ArrowRight size={14} />
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          ) : (
            <motion.div 
              key="campaign"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="max-w-6xl mx-auto space-y-12"
            >
              <div className="space-y-4">
                <h2 className="text-4xl font-extrabold tracking-tight dark:text-white flex items-center gap-3">
                  <PenTool className="text-indigo-600" size={36} />
                  Campaign Builder
                </h2>
                <p className="text-lg text-zinc-500">
                  Transforming your strategy into multi-channel assets and visuals.
                </p>
              </div>

              {loading && !campaignReport ? (
                <div className="flex flex-col items-center justify-center py-24 gap-6">
                  <div className="relative">
                    <div className="w-20 h-20 border-4 border-indigo-100 dark:border-indigo-900 rounded-full" />
                    <div className="w-20 h-20 border-4 border-t-indigo-600 rounded-full animate-spin absolute inset-0" />
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold dark:text-white">Orchestrating Agents</p>
                    <p className="text-zinc-500">Deconstructing content and generating visuals...</p>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  <div className="lg:col-span-2 space-y-8">
                    <div className="bg-white dark:bg-zinc-900 rounded-3xl p-8 shadow-lg border border-zinc-100 dark:border-zinc-800">
                      <div className="flex items-center gap-2 text-sm font-bold text-indigo-600 dark:text-indigo-400 mb-6 uppercase tracking-widest">
                        <CheckCircle2 size={16} /> Campaign Assets Ready
                      </div>
                      {campaignReport ? (
                        <div className="space-y-10">
                          <div className="space-y-4">
                            <h4 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Campaign Strategy</h4>
                            <p className="text-xl text-zinc-700 dark:text-zinc-300 font-medium leading-relaxed">
                              {campaignReport.summary}
                            </p>
                          </div>
                          
                          <div className="space-y-6">
                            <h4 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Promotional Assets</h4>
                            <div className="grid grid-cols-1 gap-6">
                              {campaignReport.assets.map((asset, i) => (
                                <div key={i} className="p-6 rounded-2xl bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-100 dark:border-zinc-700/50 space-y-4">
                                  <div className="flex items-center justify-between">
                                    <div className="px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 text-[10px] font-black uppercase">
                                      {asset.channel}
                                    </div>
                                    <h5 className="font-bold dark:text-white uppercase tracking-tighter text-sm">{asset.title}</h5>
                                  </div>
                                  <p className="text-sm dark:text-zinc-300 font-mono whitespace-pre-wrap leading-relaxed opacity-80">
                                    {asset.content}
                                  </p>
                                  <div className="pt-4 border-t border-zinc-100 dark:border-zinc-700/50">
                                    <p className="text-[10px] font-bold text-zinc-400 uppercase mb-1">Visual Direction</p>
                                    <p className="text-xs text-indigo-600 dark:text-indigo-400 italic">"{asset.visual_suggestion}"</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="py-20 text-center text-zinc-400">Select a topic from Strategy to generate a campaign.</div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-8">
                    <div className="bg-white dark:bg-zinc-900 rounded-3xl p-6 shadow-lg border border-zinc-100 dark:border-zinc-800">
                      <h3 className="text-lg font-bold mb-6 flex items-center gap-2 dark:text-white">
                        <ImageIcon size={20} className="text-indigo-600" /> Visual Assets
                      </h3>
                      <div className="grid grid-cols-1 gap-4">
                        {images.length > 0 ? images.map((src, i) => (
                          <motion.div 
                            key={i}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: i * 0.1 }}
                            className="aspect-[16/9] rounded-2xl overflow-hidden bg-zinc-100 dark:bg-zinc-800 border dark:border-zinc-700 group cursor-zoom-in"
                          >
                            <img src={src} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" alt="Generated campaign visual" />
                          </motion.div>
                        )) : (
                          <div className="aspect-[16/9] rounded-2xl border-2 border-dashed border-zinc-200 dark:border-zinc-800 flex flex-col items-center justify-center text-zinc-400 p-8 text-center">
                            <ImageIcon size={32} className="mb-2 opacity-20" />
                            <p className="text-xs font-medium">Visuals will appear here after generation</p>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-3xl p-8 text-white shadow-xl shadow-indigo-500/20">
                      <h4 className="font-bold text-lg mb-2">Campaign Ready!</h4>
                      <p className="text-indigo-100 text-sm mb-6 leading-relaxed">All generated assets are locked and synced for 2026 deployment.</p>
                      <button className="w-full py-4 bg-white text-indigo-700 rounded-2xl font-extrabold shadow-sm hover:bg-indigo-50 transition-colors">
                        Deploy Campaign
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
